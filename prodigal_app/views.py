from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
from django.db import connection
from os import urandom
from base64 import b64encode
import hashlib
import requests
from . import nasdaq_scraper


# Create your views here.
def index(request):
    """
    Renders index page from template. If session is remained, redirect to profile.
    :param request: request from user
    :return: rendered html
    """
    if request.session.get("user_id") is not None:
        return redirect('profile')
    return render(request, "index.html")


def profile(request):
    """
    Renders profile page from template. Profile page is only accessible if authenticated.
    :param request: request from user
    :return: rendered html
    """
    user_id = request.session.get('user_id')
    if user_id is None:  # If user_id not present in session, it is an invalid access.
        request.session.flush()  # Clear all session data
        return redirect('login')
    return_dict = {}
    cursor = connection.cursor()
    # Update history, favorites to reflect changes real time
    if request.session.get('first_login'):
        history = request.session.get('history')
        favorites = request.session.get('favorites')
    else:
        cursor.execute("SELECT history, favorites FROM User WHERE userID = %s", [user_id])
        row = cursor.fetchone()
        history = row[0]
        favorites = row[1]
    # Handle history data
    if history is not None:  # History data exist in database
        history_arr = []
        hist_cid_arr = history.split(',')
        for cid in hist_cid_arr:
            cursor.execute("SELECT Symbol, Name FROM Nasdaq_Companies WHERE companyID = %s", [cid])
            row = cursor.fetchone()
            ticker = row[0]
            company_name = row[1]
            history_arr.append((ticker, company_name))
        return_dict['history'] = history_arr  # List of tuples of ticker and company name
    # Handle favorites data
    if favorites is not None:  # Favorite data exist in database
        favorite_arr = []
        fav_cid_arr = favorites.split(',')
        for cid in fav_cid_arr:
            cursor.execute("SELECT Symbol, Name FROM Nasdaq_Companies WHERE companyID = %s", [cid])
            row = cursor.fetchone()
            ticker = row[0]
            company_name = row[1]
            favorite_arr.append((ticker, company_name))
        return_dict['favorites'] = favorite_arr  # List of tuples of ticker and company name
    request.session['first_login'] = False
    return render(request, 'profile.html', return_dict)


def login_query(request):
    """
    Queries username and password to database and redirect to profile if match found, alert and return to login page
    when match is not found.
    :param request: request from user
    :return: calls profile if match, login if mismatch
    """
    username = request.POST.get('username')
    password = request.POST.get('password')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM User WHERE username=%s", [username])
    row = cursor.fetchone()
    if row is None:  # User doesn't exit
        messages.add_message(request, messages.INFO, 'Login Failed!')
        return redirect('login')
    # Check password hash
    salt = row[5]
    input_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    if row[4] != input_hash:  # Invalid password
        messages.add_message(request, messages.INFO, 'Login Failed!')
        return redirect('login')
    # Update session to pass to profile
    request.session['user_id'] = int(row[0])
    request.session['username'] = row[1]
    request.session['email'] = row[2]
    request.session['gender'] = row[3]
    request.session['history'] = row[6]
    request.session['favorites'] = row[7]
    request.session['first_login'] = True
    return redirect('profile')


def login(request):
    """
    Renders login page from template. Login page will only accept 3rd-party auth.
    :param request: request from user
    :return: rendered html
    """
    if request.session.get("user_id") is not None:
        return redirect('profile')
    return render(request, "login.html")


def signout(request):
    """
    Clears session data and redirect to index page.
    :param request: request from user
    :return: rendered html
    """
    request.session.flush()
    return redirect('index')


def create_user(request):
    """
    Create a user with given username, email address and password. 
    Signup fail if customer leave any line blank or have same username with others.
    :param request: request from user
    :return: profile page if signup succeed and automatically login, stay signup and show error message if fail
    """
    username = request.POST.get('username', '')
    email = request.POST.get('email', '')
    password = request.POST.get('password', '')
    gender = request.POST.get('gender', '')
    # fail if blank
    if username == '':
        messages.add_message(request, messages.INFO, 'username is required')
        return render(request, "Signup.html")
    elif email == '':
        messages.add_message(request, messages.INFO, 'email is required')
        return render(request, "Signup.html")
    elif password == '':
        messages.add_message(request, messages.INFO, 'password is required')
        return render(request, "Signup.html")
    with connection.cursor() as cursor:
        cursor.execute("SELECT userID FROM User WHERE username = %s or email = %s", [username, email])
        user_id = cursor.fetchone()
        # fail if username/email is used
        if user_id is not None:
            messages.add_message(request, messages.INFO, 'Username/Email is already used.')
            return redirect("signup.html")
        salt = b64encode(urandom(48)).decode()
        hashed_pw = hashlib.sha256((salt + password).encode()).hexdigest()
        cursor.execute("INSERT INTO User VALUES(NULL, %s, %s, %s, %s, %s, NULL, NULL)",
                       [username, email, gender, hashed_pw, salt])
        # Redirect to login page
        messages.add_message(request, messages.INFO, 'Account created!')
        return render(request, "login.html")


def signup(request):
    """
    Renders signup page from template. Signup process links 3rd-party auth data with prodigal profile.
    :param request: request from user
    :return: rendered html
    """
    if request.session.get("user_id") is not None:
        return redirect('profile')
    return render(request, "signup.html")


def search(request):
    """
    Query user input of ticker symbol to database, then uses API and scraper to fetch data.
    Renders search page from template, filled with fetched data.
    If symbol doesn't match in database, render page notifying user no result found.
    :param request: request from user
    :return: rendered html
    """
    user_id = request.session.get('user_id', '')
    ticker = request.POST.get('search_key', '')
    ticker = ticker.capitalize()
    # get companyID by ticker
    with connection.cursor() as cursor:
        cursor.execute("SELECT companyID FROM Nasdaq_Companies WHERE Symbol = %s", [ticker])
        company_id = cursor.fetchone()  # returned row
        if company_id is None:  # No matching company found
            return render(request, "search.html", {"msg": "No Matching Result."})
        company_id = company_id[0]  # pick value from row
        cursor.execute("SELECT history FROM User WHERE userID = %s", [user_id])
        # cid1, cdi2, cid3, cid4, cid5
        # cid1 is the newest and cid5 is the oldest
        result = cursor.fetchone()
        if result[0] is not None:
            history = result[0]
            h = history.split(',')
            # history search less than 5
            if len(h) < 5:
                # compare the most recent one with search result this term
                if h[0] != company_id:
                    history = str(company_id) + ',' + history
            # more than 5 history
            else:
                # compare the most recent one with search result this term
                if h[0] != company_id:
                    history = str(company_id) + ',' + h[0] + ',' + h[1] + ',' + h[2] + ',' + h[3]
        else:
            history = str(company_id)
        # update search history
        cursor.execute("UPDATE User SET history = %s WHERE userID = %s", [history, user_id])
    # If company is in database, start scraper
    news_list, company_desc, company_name = nasdaq_scraper.scrape(ticker)
    # use ticker symbol to get info when API gets done
    url = "http://prodigal-ml.us-east-2.elasticbeanstalk.com/stocks/" + ticker + "/?ordering=-date&format=json"
    response = requests.get(url)
    if response.status_code == 404:  # company not found in api
        return_dict = dict(newslist=news_list, desc=company_desc, name=company_name)
    else:
        company_json = response.json()[0]  # company_json now holds dictionary created by json data
        return_dict = dict(newslist=news_list, desc=company_desc, name=company_name, high=company_json["high"],
                           low=company_json["low"], opening=company_json["opening"], closing=company_json["closing"],
                           volume=company_json["volume"])
    return render(request, "search.html", return_dict)


def receive_token(request):
    """
    Renders profile page after receiving user auth ID token.
    :param request: requeset from user
    :return: rendered html
    """
    return render(request, "profile.html")


