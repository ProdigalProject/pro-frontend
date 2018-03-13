from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
from django.db import connection
import requests
from . import nasdaq_scraper
from prodigal_app.models import *


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
    # Update history, favorites to reflect changes real time
    if request.session.get('first_login'):
        history = request.session.get('history')
        favorites = request.session.get('favorites')
    else:
        user_obj = User.objects.get(userid=user_id)
        history = user_obj.history
        favorites = user_obj.favorites
    # Handle history data
    if history is not None:  # History data exist in database
        history_arr = []
        hist_cid_arr = history.split(',')
        for cid in hist_cid_arr:
            company_obj = NasdaqCompanies.objects.get(companyid=cid)
            ticker = company_obj.symbol
            company_name = company_obj.name
            history_arr.append((ticker, company_name))
        return_dict['history'] = history_arr  # List of tuples of ticker and company name
    # Handle favorites data
    if favorites is not None:  # Favorite data exist in database
        favorite_arr = []
        fav_cid_arr = favorites.split(',')
        for cid in fav_cid_arr:
            company_obj = NasdaqCompanies.objects.get(companyid=cid)
            ticker = company_obj.symbol
            company_name = company_obj.name
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
    # Try login
    user_obj = User.verify_login(username, password)
    if user_obj is None:  # login failed
        messages.add_message(request, messages.INFO, 'Login Failed!')
        return redirect('login')
    # Update session to pass to profile
    request.session['user_id'] = int(user_obj.userid)
    request.session['username'] = user_obj.username
    request.session['email'] = user_obj.email
    request.session['gender'] = user_obj.gender
    request.session['history'] = user_obj.history
    request.session['favorites'] = user_obj.favorites
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
    # Create user using given values
    signup_status = User.create_user(username, email, gender, password)
    if signup_status == 1:
        # Username / email already used
        messages.add_message(request, messages.INFO, 'Username/Email is already used.')
        return redirect('signup')
    else:
        # Redirect to login page
        messages.add_message(request, messages.INFO, 'Account created!')
        return redirect('login')


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
    if request.session.get("user_id") is None:
        return redirect('login')
    user_id = request.session.get('user_id', '')
    user_obj = User.objects.get(userid=user_id)
    ticker = request.POST.get('search_key', '')
    ticker = ticker.capitalize()
    # get companyID by ticker
    try:
        company_obj = NasdaqCompanies.objects.get(symbol=ticker)
    except NasdaqCompanies.DoesNotExist:
        return render(request, "search.html", {"msg": "No Matching Result."})
    # update search history
    user_obj.update_history(company_obj.companyid)
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
    request.session['last_search'] = company_obj.companyid  # For use in favorites
    return render(request, "search.html", return_dict)


def receive_token(request):
    """
    Renders profile page after receiving user auth ID token.
    :param request: request from user
    :return: rendered html
    """
    return render(request, "profile.html")


def favorite(request):
    """
    Only called when first displaying the favorite button. Checks if currently displaying company is in favorite
    list and display favorite button or unfavorite button.
    :param request: request from user
    :return: rendered html
    """
    favorite_list = request.session.get('favorites')
    print(favorite_list)
    if favorite_list is None:
        return render(request, "favorite_btn.html", {'favorited': False})
    favorite_list = favorite_list.split(',')
    last_search = request.session.get('last_search')
    return_dict = {}
    if last_search in favorite_list:
        return_dict['favorited'] = True
    else:
        return_dict['favorited'] = False
    return render(request, "favorite_btn.html", return_dict)


def add_favorite(request):
    """
    Adds favorite company to database. This function only renders a button to iframe in search page.
    :param request: request from user
    :return: rendered html
    """
    user_id = request.session.get('user_id')
    company_id = request.session.get('last_search')
    favorite_list = request.session.get('favorites')
    if favorite_list is None:
        favorite_list = str(company_id)
    else:
        favorite_list = favorite_list + ',' + company_id
    print(favorite_list)
    request.session['favorites'] = favorite_list
    cursor = connection.cursor()
    cursor.execute("UPDATE User SET favorites = %s WHERE userID = %s", [favorite_list, user_id])
    return render(request, "favorite_btn.html", {'favorited': True})


def remove_favorite(request):
    """
    Removes favorite company from database. This function only renders a button to iframe in search page.
    :param request: request from user
    :return: rendered html
    """
    user_id = request.session.get('user_id')
    company_id = request.session.get('last_search')
    favorite_list = request.session.get('favorites')
    if favorite_list is None:
        return render(request, "favorite_btn.html")
    else:
        favorite_list.replace(',' + str(company_id), '')
    print(favorite_list)
    request.session['favorites'] = favorite_list
    cursor = connection.cursor()
    cursor.execute("UPDATE User SET favorites = %s WHERE userID = %s", [favorite_list, user_id])
    return render(request, "favorite_btn.html", {'favorited': False})
