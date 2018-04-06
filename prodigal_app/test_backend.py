#!/home/gitlab-runner/builds/b74f8bb5/0/prodigal/pro-frontend/venv/bin/python3
from django.test import TestCase
import django
from prodigal_app.models import NasdaqCompanies, User, SearchUtility
from prodigal_app.nasdaq_scraper import  *


class NasdaqScraperTestCase(TestCase):
    def test_sreaper(self):
        django.setup()
        news,data = scrape("AAPL")
        assert 0 < len(news) <= 5
        assert news is not None


class NasdaqCompaniesTestCase(TestCase):
    def setUp(self):
        # self.test_company = NasdaqCompanies( symbol = "TEST", name = "Test name Inc.", sector = "Test")
        comp_obj = NasdaqCompanies(symbol = "TEST", name = "Test name Inc.", sector = "Test")
        comp_obj.save()

    def test_company_exist(self):
        self.assertTrue(NasdaqCompanies.objects.filter(symbol="TEST").exists())


class UserTestCase(TestCase):
    def setUp(self):
        self.test_user = User(username="test", email="test8888@gmail.com", gender="male", password="1234", salt="4321")
        self.test_company = NasdaqCompanies(symbol="AAPL", name="Apple Inc.", sector="Test",companyid="123")
        self.test_company_2 = NasdaqCompanies(symbol="AMZN", name="Amazon Inc.", sector="Test",companyid="888")
        self.test_company.save()
        self.test_company_2.save()
        self.test_user.save()
        self.test_user_search = SearchUtility()

    def test_create_user(self):
        assert self.test_user.create_user("test","test@gmail.com","male","1234") == 1
        assert self.test_user.create_user("testab", "test235@gmail.com", "male", "1234") == 0

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
        self.test_user.update_history("888")
        self.test_user.update_history("888")
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

    def test_prediction(self):
        array = self.test_user_search.pridict("AAPL")
        assert array is not None
