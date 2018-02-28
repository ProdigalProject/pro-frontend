from django.shortcuts import render
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


def login(request):
    """
    Renders login page from template. Login page will only accept 3rd-party auth.
    :param request: request from user
    :return: rendered html
    """
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
    news_list, company_desc, company_name = nasdaq_scraper.scrape(request.POST.get('search_key',''))
    return render(request, "search.html", {"newslist": news_list, "desc": company_desc, "name":company_name})


def receive_token(request):
    """
    Renders profile page after receiving user auth ID token.
    :param request: requeset from user
    :return: rendered html
    """
    return render(request, "profile.html")


