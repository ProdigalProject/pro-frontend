from django.test import TestCase
from prodigal_app.models import NasdaqCompanies, User, SearchUtility
from prodigal_app.nasdaq_scraper import *


class NasdaqScraperTestCase(TestCase):
    def test_sreaper(self):
        """
        Tests if scraper succeeds in scraping news.
        """
        news, data = scrape("AAPL")
        assert 0 < len(news) <= 5
        assert news is not None


class NasdaqCompaniesTestCase(TestCase):
    def setUp(self):
        comp_obj = NasdaqCompanies(
            symbol="TEST", name="Test name Inc.", sector="Test")
        comp_obj.save()

    def test_company_exist(self):
        """
        Tests if company is properly added to database.
        """
        self.assertTrue(NasdaqCompanies.objects.filter(symbol="TEST").exists())


class UserTestCase(TestCase):
    def setUp(self):
        self.test_user = User(
            username="test", email="test8888@gmail.com",
            gender="male", password="1234", salt="4321")
        self.test_company = NasdaqCompanies(
            symbol="AAPL", name="Apple Inc.",
            sector="Test", companyid="123")
        self.test_company_2 = NasdaqCompanies(
            symbol="AMZN", name="Amazon Inc.",
            sector="Test", companyid="888")
        self.test_company.save()
        self.test_company_2.save()
        self.test_user.save()
        self.test_user_search = SearchUtility()

    def test_create_user(self):
        """
        Tests creating user in database. Also checks if using existing
        username fails properly.
        """
        assert self.test_user.create_user(
            "test", "test@gmail.com", "male", "1234") == 1
        assert self.test_user.create_user(
            "testab", "test235@gmail.com", "male", "1234") == 0

    def test_verify_valid_email(self):
        """
        Tests email verification using valid email address format.
        """
        result = User.validate_email('test@gmail.com')
        self.assertTrue(result)

    def test_verify_invalid_email(self):
        """
        Tests email verification using invalid email address format.
        """
        self.assertFalse(User.validate_email('test'))
        self.assertFalse(User.validate_email('test@gmail'))
        self.assertFalse(User.validate_email('test@.com'))

    def test_verify_login(self):
        """
        Tests login verification with valid credentials.
        """
        User.create_user("test10", "test10@gmail.com", "male", "1234")
        result = User.verify_login("test10", "1234")
        self.assertIsNotNone(result)

    def test_verify_invalid_login(self):
        """
        Tests login verification with invalid credentials.
        """
        result = User.verify_login("testinv", "1234")
        self.assertIsNone(result)

    def test_favorite(self):
        """
        Tests adding to / removing from favorites list.
        """
        self.test_user.add_favorite("AAPL")
        self.test_user.add_favorite("AMZN")
        array = self.test_user.get_favorite()
        assert ('AAPL', 'Apple Inc.') in array
        self.test_user.remove_favorite("AAPL")
        array = self.test_user.get_favorite()
        assert ('AAPL', 'Apple Inc.') not in array

    def test_history(self):
        """
        Tests updating and retrieving history list.
        """
        assert self.test_user.get_history() is None
        self.test_user.update_history("123")
        self.test_user.update_history("888")
        self.test_user.update_history("888")
        array = self.test_user.get_history()
        assert ('AAPL', 'Apple Inc.') in array

    def test_search_not_found(self):
        """
        Tests searching on non-existing company.
        """
        data, symbol = self.test_user_search.nasdaq_search("XYZ")
        assert symbol is None

    def test_search_found(self):
        """
        Tests searching on existing company.
        """
        data, symbol = self.test_user_search.nasdaq_search("AAPL")
        assert symbol == "AAPL"

    def test_search_by_sector(self):
        """
        Tests if search_by_sector returns proper results.
        """
        array = self.test_user_search.search_by_sector("Test")
        assert ('Apple Inc.', 'AAPL') in array

    def test_prediction(self):
        """
        Tests if getting prediction data works properly.
        """
        array = self.test_user_search.predict("AAPL")
        assert array is not None
