# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create,
#   * modify, and delete the table
# Feel free to rename the models,
# but don't rename db_table values or field names.
from django.db import models
from os import urandom
from base64 import b64encode
from . import nasdaq_scraper
import hashlib
import requests


class NasdaqCompanies(models.Model):
    """
    Model for companies listed in Nasdaq market.
    """
    # Field name made lowercase.
    companyid = models.AutoField(db_column='companyID', primary_key=True)
    # Field name made lowercase.
    symbol = models.CharField(db_column='Symbol', max_length=5)
    # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=75)
    # Field name made lowercase.
    sector = models.CharField(db_column='Sector', max_length=50)

    class Meta:
        managed = True
        db_table = 'Nasdaq_Companies'


class User(models.Model):
    """
    Model for user. All user related actions will be taken care by this class.
    """
    # Field name made lowercase.
    userid = models.AutoField(db_column='userID', primary_key=True)
    username = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    gender = models.CharField(max_length=6)
    password = models.CharField(max_length=100)
    salt = models.CharField(max_length=100)
    history = models.TextField(blank=True, null=True)
    favorites = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'User'

    @staticmethod
    def create_user(username, email, gender, pw):
        """
        Creates new user from input.
        Class doesn't need to be instantiated before calling this function.
        :param username: username of new user
        :param email: email address of new user
        :param gender: gender of new user (Male, Female, Other)
        :param pw: password of new user
        :return: 0 on success, 1 on fail
        """
        # Check if username / email already used
        if User.objects.filter(username=username) or User.objects.filter(
                email=email):
            return 1
        salt = b64encode(urandom(48)).decode()
        hashed_pw = hashlib.sha256((salt + pw).encode()).hexdigest()
        user_obj = User(username=username, email=email,
                        gender=gender, password=hashed_pw, salt=salt)
        # TODO: email verification require

        user_obj.save()
        return 0

    @staticmethod
    def verify_login(username, pw):
        """
        Verifies given login credentials.
        Class doesn't need to be instantiated before calling this function.
        :param username: username input from view
        :param pw: password input from view
        :return: User object on success, None on fail
        """
        try:
            user_obj = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        # Check password hash
        salt = user_obj.salt
        input_hash = hashlib.sha256((salt + pw).encode()).hexdigest()
        if user_obj.password != input_hash:  # Invalid password
            return None
        return user_obj

    def get_favorite(self):
        """
        Returns list of favorites to view.
        :return: None or list of tuples (symbol, company_name)
        """
        if self.favorites is None:
            return None
        else:
            favorite_arr = []
            fav_cid_arr = self.favorites.split(',')
            for cid in fav_cid_arr:
                company_obj = NasdaqCompanies.objects.get(companyid=cid)
                ticker = company_obj.symbol
                company_name = company_obj.name
                favorite_arr.append((ticker, company_name))
            return favorite_arr

    def add_favorite(self, ticker):
        """
        Adds given company into favorites list.
        :param ticker: Ticker symbol of company passed in from view
        :return: no return value.
        """
        company_obj = NasdaqCompanies.objects.get(symbol=ticker)
        if self.favorites is None:
            self.favorites = str(company_obj.companyid)
        else:
            self.favorites = self.favorites + ',' + str(company_obj.companyid)
        self.save()

    def remove_favorite(self, ticker):
        """
        Removes company from favorites list.
        :param ticker: Ticker symbol of company passed in from view
        :return: no return value.
        """
        company_obj = NasdaqCompanies.objects.get(symbol=ticker)
        fav_list = self.favorites.split(',')
        fav_list.remove(str(company_obj.companyid))
        if len(fav_list) == 0:
            self.favorites = None
        else:
            self.favorites = ','.join(fav_list)
        self.save()

    def get_history(self):
        """
        Returns list of search history to view.
        :return: None or list of tuples (symbol, company_name)
        """
        if self.history is None:
            return None
        else:
            history_arr = []
            hist_cid_arr = self.history.split(',')
            for cid in hist_cid_arr:
                company_obj = NasdaqCompanies.objects.get(companyid=cid)
                ticker = company_obj.symbol
                company_name = company_obj.name
                history_arr.append((ticker, company_name))
            return history_arr

    def update_history(self, company_id):
        """
        Updates history field with given company_id.
        :param company_id: company_id passed from view
        :return: no return value
        """
        if self.history is None:
            history = str(company_id)
        else:
            history = self.history
            h = history.split(',')
            # history search less than 5
            if len(h) < 5:
                # compare the most recent one with search result this term
                if int(h[0]) != company_id:
                    history = str(company_id) + ',' + history
            # more than 5 history
            else:
                # compare the most recent one with search result this term
                if int(h[0]) != company_id:
                    history = str(company_id) + ',' + h[0] + ','\
                              + h[1] + ',' + h[2] + ',' + h[3]
        self.history = history
        self.save()


class SearchUtility(User):
    """
    Class to handle searches.
    Since search function doesn't need its own table
    and updates history field of User.
    it is made a proxy class of User class.
    """
    class Meta:
        proxy = True

    def nasdaq_search(self, ticker):
        """
        Query user input of ticker symbol to database,
        then uses API and scraper to fetch data.
        Search history is also updated.
        :param ticker: ticker symbol passed in from view.
        :return: None if no match,
        dictionary of required data if match is found
        """
        # get companyID by symbol
        try:
            company_obj = NasdaqCompanies.objects.get(symbol=ticker)
        except NasdaqCompanies.DoesNotExist:  # ticker not in company list
            return None, None
        # update search history
        self.update_history(company_obj.companyid)
        # start scraper
        news_list, company_desc = nasdaq_scraper.scrape(ticker)
        # use ticker symbol to get info from API
        # TODO: duplicate data
        url = "https://prodigal-ml.azurewebsites.net" \
              "/stocks/" + ticker + "/?ordering=-date&format=json"
        response = requests.get(url)
        if response.status_code == 404:  # company not found in api
            return_dict = dict(newslist=news_list,
                               desc=company_desc, name=company_obj.name)
        else:
            chart_json = response.json()
            latest_data = chart_json[0]  # latest data
            return_dict = dict(newslist=news_list, desc=company_desc,
                               name=company_obj.name, high=latest_data["high"],
                               low=latest_data["low"],
                               opening=latest_data["opening"],
                               closing=latest_data["closing"],
                               volume=latest_data["volume"],
                               latest_date=latest_data["date"],
                               chart_json=chart_json)
        return return_dict, company_obj.symbol

    def search_by_sector(self, sector_symbol):
        """
        Query user input of sector to database.
        Search history is also updated if click the button in the return list.
        :param sector_symbol: sector passed in from view.
        :return: None if no match, list of required data if match is found
        """
        try:
            company_list = NasdaqCompanies.objects.filter(sector=sector_symbol)
        except NasdaqCompanies.DoesNotExist:  # sector not in company list
            return None
        # return tuple list (name, ticker)
        return_list = []
        for company in company_list:
            company_name = company.name
            company_sym = company.symbol
            temp = (company_name, company_sym)
            return_list.append(temp)
        return return_list

    def pridict(self, ticker):
        """
        Query pridiction data from api service by ticker.
        :param ticker: ticker symbol passed in from view.
        :return: None if no data proviede,
        list of following five days closing price if found
        """
        url = "https://prodigal-ml.a" \
              "zurewebsites.net/stocks/" + ticker + "/runexpr"
        response = requests.get(url)
        if response.status_code == 404:  # company not found in api
            return None
        else:
            pridiction = response.json()
            return pridiction

    def getCompaniesName(self):
        """
        Query all company names from database.
        :param None
        :return: None if no data proviede,
        list of company name
        """
        # list for all companies name
        company_list = []
        company_obj_all = NasdaqCompanies.objects.values_list('name', flat=True)
        company_obj_all = company_obj_all.distinct()  # get all tickers
        for company in company_obj_all:
            company_list.append(company)
        return company_list

    def getTickerByName(self, search_name):
        """
        Query company ticker from database by name.
        :param search_name: key name
        :return: None if no data proviede,
        company ticker
        """
        print(search_name)
        try:
            company_ticker = NasdaqCompanies.objects.get(name=search_name).symbol
        except NasdaqCompanies.DoesNotExist:  # ticker not in company list
            return None
        return company_ticker