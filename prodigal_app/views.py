from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
from prodigal_app.models import *


def index(request):
    """
    Renders index page from template.
    If session is remained, redirect to profile.
    :param request: request from user
    :return: rendered html
    """
    if request.session.get("user_id") is not None:
        return redirect('profile')
    return render(request, "index.html")


def profile(request):
    """
    Renders profile page from template.
    Profile page is only accessible if authenticated.
    :param request: request from user
    :return: rendered html
    """
    user_id = request.session.get('user_id')
    # If user_id not present in session, it is an invalid access.
    if user_id is None:
        request.session.flush()  # Clear all session data
        return redirect('login')

    # get company list for further use
    user_obj = SearchUtility.objects.get(userid=user_id)
    company_list = user_obj.get_companies_name()

    return_dict = {}
    # Update history, favorites to reflect changes real time
    if request.session.get('first_login'):  # First visiting profile
        history_arr = request.session.get('history')
        return_dict['history'] = history_arr
        favorite_arr = request.session.get('favorites')
        return_dict['favorites'] = favorite_arr
    # Not first visiting profile; history/favorite in session might be old
    else:
        user_obj = User.objects.get(userid=user_id)
        history_arr = user_obj.get_history()
        # List of tuples of ticker and company name
        return_dict['history'] = history_arr
        favorite_arr = user_obj.get_favorite()
        # List of tuples of ticker and company name
        return_dict['favorites'] = favorite_arr
    request.session['first_login'] = False
    return_dict["company_list"] = company_list
    return render(request, 'profile.html', return_dict)


def login_query(request):
    """
    Queries username and password to database and redirect to profile
    if match found, alert and return to login page
    when match is not found.
    :param request: request from user
    :return: calls profile if match, login if mismatch
    """
    username = request.POST.get('username')
    password = request.POST.get('password')
    remember = request.POST.get('remember')
    # Try login
    user_obj = User.verify_login(username, password)
    if user_obj is None:  # login failed
        messages.add_message(request, messages.INFO, 'Login Failed!')
        return redirect('login')
    # If 'Remember Me' is checked, keep session cookies for a week
    if remember is not None:
        request.session.set_expiry(604800)  # 60 * 60 * 24 * 7
    # Update session to pass to profile
    request.session['user_id'] = int(user_obj.userid)
    request.session['username'] = user_obj.username
    request.session['email'] = user_obj.email
    request.session['gender'] = user_obj.gender
    request.session['history'] = user_obj.get_history()
    request.session['favorites'] = user_obj.get_favorite()
    request.session['first_login'] = True
    return redirect('profile')


def login(request):
    """
    Renders login page from template.
    Login page will only accept 3rd-party auth.
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
    Signup fails if any of the POST input is blank or have same
    username / email with others.
    :param request: request from user
    :return: profile page if signup succeed and automatically login,
    stay signup and show error message if fail
    """
    username = request.POST.get('username', '')
    email = request.POST.get('email', '')
    password = request.POST.get('password', '')
    gender = request.POST.get('gender', '')
    # fail if blank
    if username == '':
        messages.add_message(request, messages.INFO, 'Username is required')
        return render(request, "Signup.html")
    elif email == '':
        messages.add_message(request, messages.INFO, 'Email is required')
        return render(request, "Signup.html")
    elif User.validate_email(email) is False:
        messages.add_message(request, messages.INFO, 'Email is invalid')
        return render(request, "Signup.html")
    elif password == '':
        messages.add_message(request, messages.INFO, 'Password is required')
        return render(request, "Signup.html")
    # Create user using given values
    signup_status = User.create_user(username, email, gender, password)
    if signup_status == 1:
        # Username / email already used
        messages.add_message(request, messages.INFO,
                             'Username/Email is already used.')
        return redirect('signup')
    else:
        # Redirect to login page
        messages.add_message(request, messages.INFO, 'Account created!')
        User.welcome_email(email, username)
        return redirect('login')


def signup(request):
    """
    Renders signup page from template. signup.html contains a form that
    posts gender, username, password and email input.
    :param request: request from user
    :return: rendered html
    """
    if request.session.get("user_id") is not None:
        return redirect('profile')
    return render(request, "signup.html")


def search(request):
    """
    Renders search page from template, filled with fetched data.
    If no match is found in search, render page notifying user no result found.
    Sector search is also handled in this function.
    If mode is set to comparison, compare_company function is called.
    :param request: request from user
    :return: rendered html
    """
    if request.session.get("user_id") is None:
        return redirect('login')

    user_id = request.session.get('user_id', '')
    user_obj = SearchUtility.objects.get(userid=user_id)
    company_search = request.POST.get('search_key', '')
    mode = request.POST.get('mode', '')
    # get company list for further use
    company_list = user_obj.get_companies_name()

    # search by sector
    if 'sector = ' in company_search:
        sector_symbol = company_search.lstrip("sector = ")
        result_list = user_obj.search_by_sector(sector_symbol)
        if result_list is None:
            return render(request, "sector.html",
                          {"msg": "Sector didn't find.",
                           "company_list": company_list})
        return_dict = dict()
        return_dict["list"] = result_list
        return_dict["sector"] = sector_symbol
        return_dict["company_list"] = company_list
        return render(request, "sector.html", return_dict)
    # search/compare by ticker/company name
    else:
        ticker = user_obj.get_ticker_by_name(company_search)
        if ticker is None:
            return render(request, "search.html",
                          {"msg": "No Matching Result.",
                           "company_list": company_list})
        # search for new company
        if 'comparison' not in mode:
            # search first and create a record endpoint
            return_dict, company_sym = user_obj.nasdaq_search(ticker)
            # get pridiction for further use
            pridiction = user_obj.predict(ticker)
            if return_dict is None:
                return render(request, "search.html",
                              {"msg": "No Matching Result.",
                               "company_list": company_list})
            request.session["last_search"] = company_sym  # For favorites
            if pridiction is not None:
                return_dict["pridiction"] = pridiction
            return_dict["company_list"] = company_list
            return render(request, "search.html", return_dict)
        # compare companies
        else:
            return compare_company(
                request, mode, user_obj, ticker, company_list)


def compare_company(request, mode, user_obj, ticker, company_list):
    """
    Helper function extracted from search for comparison feature.
    :param request: request from user.
    :param mode: mode of search, from POST
    :param user_obj: user object of currently logged in user
    :param ticker: ticker symbol of company to compare
    :param company_list: list of companies in database
    :return: rendered html
    """
    # get first company (base company) data
    first_dict, company_sym_first = \
        user_obj.nasdaq_search(request.session.get('last_search'))
    # get pridiction for further use
    pridiction = user_obj.predict(request.session.get('last_search'))
    if first_dict is None:  # no first company match
        return render(request, "search.html",
                      {"msg": "No Comparison Object.",
                       "company_list": company_list})
    # get second company data
    second_dict, company_sym_second = user_obj.nasdaq_search(ticker)
    if company_sym_first == company_sym_second:
        first_dict["pridiction"] = pridiction
        first_dict["company_list"] = company_list
        return render(request, "search.html", first_dict)
    pridiction_second = user_obj.predict(ticker)
    if second_dict is None:  # no second compant match
        if pridiction is not None:
            first_dict["pridiction"] = pridiction
            first_dict["company_list"] = company_list
        return render(request, "search.html", first_dict)
    return_dict = first_dict.copy()
    return_dict["name_second"] = second_dict["name"]
    return_dict["chart_json_second"] = second_dict["chart_json"]
    if pridiction is not None:
        return_dict["pridiction"] = pridiction
    if pridiction_second is not None:
        return_dict["pridiction_second"] = pridiction_second
    return_dict["company_list"] = company_list
    return_dict["mode"] = mode
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
    Only called when first displaying the search page. Checks if currently
    displaying company is in favorite list and display favorite button or
    unfavorite button.
    :param request: request from user
    :return: rendered html
    """
    favorite_list = request.session.get('favorites')
    if favorite_list is None:
        return render(request, "favorite_btn.html", {'favorited': False})
    last_search = request.session.get('last_search')
    return_dict = {}
    for (sym, name) in favorite_list:
        if sym == last_search:
            return_dict['favorited'] = True
            return render(request, "favorite_btn.html", return_dict)
    # Not in favorites list
    return_dict['favorited'] = False
    return render(request, "favorite_btn.html", return_dict)


def add_favorite(request):
    """
    Adds favorite company to database. This function only renders a button to
    iframe in search page.
    :param request: request from user
    :return: rendered html
    """
    user_id = request.session.get('user_id')
    user_obj = User.objects.get(userid=user_id)
    company_sym = request.session.get('last_search')
    user_obj.add_favorite(company_sym)
    request.session['favorites'] = user_obj.get_favorite()
    msg = EmailMessage(
        ' ' + company_sym + ' has been added to your favorites',
        '<img src="https://prodigal-beta.azurewebsites.net/'
        'static/images/main_logo.png">',
        'prodigalapp@gmail.com',
        [request.session.get('email')],
        )
    msg.content_subtype = "html"
    msg.send(fail_silently=True)
    return render(request, "favorite_btn.html", {'favorited': True})


def remove_favorite(request):
    """
    Removes favorite company from database. This function only renders a
    button to iframe in search page.
    :param request: request from user
    :return: rendered html
    """
    user_id = request.session.get('user_id')
    user_obj = User.objects.get(userid=user_id)
    company_sym = request.session.get('last_search')
    user_obj.remove_favorite(company_sym)
    request.session['favorites'] = user_obj.get_favorite()
    msg = EmailMessage(
        ' ' + company_sym + ' has been removed from your favorites',
        '<img src="https://prodigal-beta.azurewebsites.net/'
        'static/images/main_logo.png">',
        'prodigalapp@gmail.com',
        [request.session.get('email')],
        )
    msg.content_subtype = "html"
    msg.send(fail_silently=True)
    return render(request, "favorite_btn.html", {'favorited': False})


def sector(request):
    """
    Go to sector.html. This function only render the sector html page.
    :param request: request from user
    :return: rendered html
    """
    return render(request, "sector.html")
