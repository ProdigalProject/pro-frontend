from django.test import TestCase
import django
from prodigal_app.models import *
from prodigal_app.nasdaq_scraper import  *


class NasdaqScraperTestCase(TestCase):
    def test_sreaper(self):
        news,data = scrape("AAPL")
        assert 0 < len(news) <= 5
        assert news is not None


class NasdaqCompaniesTestCase(TestCase):
    def setUp(self):
        django.setup()
        self.test_company = NasdaqCompanies( symbol = "TEST", name = "Test name Inc.", sector = "Test")

    def Test_company_exist(self):
        assert self.test_company is not None


class UserTestCase(TestCase):
    def setUp(self):
        django.setup()
        self.test_user = User(username="test", email="test@gmail.com", gender="male", password="1234", salt="4321")
        self.test_company = NasdaqCompanies(symbol="AAPL", name="Apple Inc.", sector="Test",companyid="123")
        self.test_company_2 = NasdaqCompanies(symbol="AMZN", name="Amazon Inc.", sector="Test")
        self.test_company.save()
        self.test_company_2.save()
        self.test_user.save()
        self.test_user_search = SearchUtility()

    def test_create_user(self):
        assert self.test_user.create_user("test","test@gmail.com","male","1234") == 1

    def test_verify_login(self):
        result = self.test_user.verify_login("test", "1234")
        assert self.test_user

    def test_favorite(self):
        self.test_user.add_favorite("AAPL")
        self.test_user.add_favorite("AMZN")
        array = self.test_user.get_favorite()

        #print(array)
        assert ('AAPL','Apple Inc.') in array

        self.test_user.remove_favorite("AAPL")
        array = self.test_user.get_favorite()

        assert ('AAPL', 'Apple Inc.') not in array

    def test_history(self):
        assert self.test_user.get_history() is None
        self.test_user.update_history("123")
        array = self.test_user.get_history()
        assert ('AAPL', 'Apple Inc.') in array

    def test_seach_not_found(self):
        data, symbol = self.test_user_search.nasdaq_search("XYZ")
        assert symbol is None

    def test_seach_found(self):
        data, symbol = self.test_user_search.nasdaq_search("AAPL")
        assert symbol == "AAPL"

    def test_seach_by_sector(self):
        array = self.test_user_search.search_by_sector("Test")
        assert ('Apple Inc.', 'AAPL') in array