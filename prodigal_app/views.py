from django.shortcuts import render
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
    Renders index page from template.
    :param request: request from user
    :return: rendered html
    """
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
        return render(request, 'login.html')
    username = request.session.get('username')
    email = request.session.get('email')
    gender = request.session.get('gender')
    history = request.session.get('history')
    favorites = request.session.get('favorites')
    return_dict = dict(user_id=user_id, username=username, email=email, gender=gender,
                       history=history, favorites=favorites)
    return render(request, "profile.html", return_dict)


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
        return render(request, "login.html")
    # Check password hash
    salt = row[5]
    input_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    if row[4] != input_hash:  # Invalid password
        messages.add_message(request, messages.INFO, 'Login Failed!')
        return render(request, "login.html")
    # Update session to pass to profile
    request.session['user_id'] = int(row[0])
    request.session['username'] = row[1]
    request.session['email'] = row[2]
    request.session['gender'] = row[3]
    request.session['history'] = row[6]
    request.session['favorites'] = row[7]
    return profile(request)


def login(request):
    """
    Renders login page from template. Login page will only accept 3rd-party auth.
    :param request: request from user
    :return: rendered html
    """
    return render(request, "login.html")


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
            messages.add_message(request, messages.INFO, 'username/email is used, pick another one')
            return render(request, "Signup.html")
        salt = b64encode(urandom(48)).decode()
        hashed_pw = hashlib.sha256((salt + password).encode()).hexdigest()
        cursor.execute("INSERT INTO User VALUES(NULL, %s, %s, 'Male', %s, %s, NULL, NULL)",
                       [username, email, hashed_pw, salt])
        # Redirect to login page
        messages.add_message(request, messages.INFO, 'Account created!')
        return render(request, "login.html")


def signup(request):
    """
    Renders signup page from template. Signup process links 3rd-party auth data with prodigal profile.
    :param request: request from user
    :return: rendered html
    """
    return render(request, "signup.html")


def search(request):
    """
    Renders search page from template.
    :param request: request from user
    :return: rendered html
    """
    userID = request.session.get('userID', '')
    ticker = request.POST.get('search_key', '')
    news_list, company_desc, company_name = nasdaq_scraper.scrape(ticker)
    if news_list is None:
        return render(request, "search.html", {"msg": "No Matching Result."})
    # use ticker symbol to get info when API gets done
    #url = "http://prodigal-ml.us-east-2.elasticbeanstalk.com/stocks/4/?format=json"
    #response = requests.get(url)
    #company_json = response.json()  # company_json now holds dictionary created by json data
    #return_dict = dict(newslist=news_list, desc=company_desc, name=company_name, high=company_json["high"], low=company_json["low"], opening=company_json["opening"], closing=company_json["closing"])
    return_dict = dict(newslist=news_list, desc=company_desc, name=company_name)
    # capitalize ticker
    TICKER = ticker.capitalize()
    # get companyID by ticker
    with connection.cursor() as cursor:
        cursor.execute("SELECT companyID FROM Nasdaq_Companies WHERE Symbol = %s", [TICKER])
        companyID = cursor.fetchone()
        cursor.execute("SELECT history FROM User WHERE userID = %s", [userID])
        # cid1, cdi2, cid3, cid4, cid5
        # cid1 is the newest and cid5 is the oldest
        # result = (None, )????
        result = cursor.fetchone()
        # history = (NULL)
        history = result[0]
        print (history)
        if history is not None:
            h = history.split(',')
            # history search less than 5
            if len(h) < 5:
                # compare the most recent one with search result this term
                if h[0] != companyID:
                    history = str(companyID) + ',' + history
            # more than 5 history
            else:
                # compare the most recent one with search result this term
                if h[0] != companyID:
                    history = str(companyID) + ',' + h[0] + ',' + h[1] + ',' + h[2] + ',' + h[3]
        else:
            history = str(companyID)
        # update search history
        cursor.execute("UPDATE User SET history = %s WHERE userID = %s", [history, userID])
    return render(request, "search.html", return_dict)


def receive_token(request):
    """
    Renders profile page after receiving user auth ID token.
    :param request: requeset from user
    :return: rendered html
    """
    return render(request, "profile.html")


