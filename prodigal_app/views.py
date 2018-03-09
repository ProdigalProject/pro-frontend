from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
from django.db import connection
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
    return render(request, "profile.html")


def login_query(request):
    """
    Queries username and password to database and redirect to profile if match found, alert and return to login page
    when match is not found.
    :param request: request from user
    :return: profile if match, login if mismatch
    """
    username = request.POST.get('username')
    password = request.POST.get('password')
    # TODO: Hashing and salting password
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM User WHERE username=%s AND password=%s", [username, password])
    row = cursor.fetchone()
    if row is None:
        messages.add_message(request, messages.INFO, 'Login Failed!')
        return render(request, "login.html")
    return redirect('profile')


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
        userID = cursor.fetchone()
        if userID is not None:
            messages.add_message(request, messages.INFO, 'username/email is used, pick another one')
            return render(request, "Signup.html")
        cursor.execute("INSERT INTO User VALUES(NULL, %s, %s, 'Male', %s, 'abcd', NULL, NULL)", [username, email, password])
        return redirect('profile')


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
    ticker = request.POST.get('search_key', '')
    news_list, company_desc, company_name = nasdaq_scraper.scrape(ticker)
    if news_list is None:
        return render(request, "search.html", {"msg": "No Matching Result."})
    # use ticker symbol to get info when API gets done
    url = "http://prodigal-ml.us-east-2.elasticbeanstalk.com/stocks/4/?format=json"
    response = requests.get(url)
    company_json = response.json()  # company_json now holds dictionary created by json data
    return_dict = dict(newslist=news_list, desc=company_desc, name=company_name, high=company_json["high"],
                       low=company_json["low"], opening=company_json["opening"], closing=company_json["closing"])
    return render(request, "search.html", return_dict)


def receive_token(request):
    """
    Renders profile page after receiving user auth ID token.
    :param request: requeset from user
    :return: rendered html
    """
    return render(request, "profile.html")


