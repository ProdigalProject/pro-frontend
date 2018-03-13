# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from os import urandom
from base64 import b64encode
import hashlib


class NasdaqCompanies(models.Model):
    companyid = models.AutoField(db_column='companyID', primary_key=True)  # Field name made lowercase.
    symbol = models.CharField(db_column='Symbol', max_length=5)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=75)  # Field name made lowercase.
    sector = models.CharField(db_column='Sector', max_length=50)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Nasdaq_Companies'


class User(models.Model):
    userid = models.AutoField(db_column='userID', primary_key=True)  # Field name made lowercase.
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
        Creates new user from input. Class doesn't need to be instantiated before calling this function.
        :param username: username of new user
        :param email: email address of new user
        :param gender: gender of new user (Male, Female, Other)
        :param pw: password of new user
        :return: 0 on success, 1 on fail
        """
        # Check if username / email already used
        if User.objects.filter(username=username) or User.objects.filter(email=email):
            return 1
        salt = b64encode(urandom(48)).decode()
        hashed_pw = hashlib.sha256((salt + pw).encode()).hexdigest()
        user_obj = User(username=username, email=email, gender=gender, password=hashed_pw, salt=salt)
        user_obj.save()
        return 0

    @staticmethod
    def verify_login(username, pw):
        """
        Verifies given login credentials. Class doesn't need to be instantiated before calling this function.
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

    def show_history(self):
        """
        Returns history field to view.
        :return: List of string of company ids
        """
        if self.history is None:
            return None
        else:
            return self.history.split(',')

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
                if h[0] != company_id:
                    history = str(company_id) + ',' + history
            # more than 5 history
            else:
                # compare the most recent one with search result this term
                if h[0] != company_id:
                    history = str(company_id) + ',' + h[0] + ',' + h[1] + ',' + h[2] + ',' + h[3]
        self.history = history
        self.save()
