from django.test import TestCase
import pycodestyle
import unittest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class TestSignup(unittest.TestCase):

    def setUp(self):
        """
        Stuffs to set up before running test cases.
        """
        chrome_opts = Options()
        chrome_opts.add_argument("--disable-extensions")
        chrome_opts.add_argument("--headless")
        chrome_opts.add_argument("--no-sandbox")
        chrome_opts.add_argument("--disable-gpu")
        self.driver = webdriver.Chrome(options=chrome_opts)
        self.driver.get("https://prodigal-gamma.azurewebsites.net/")

    def test_homepage_rendering(self):
        """
        Tests reaching index page.
        """
        assert "Welcome to Prodigal!" in self.driver.title

    def test_logo_return_to_homepage(self):
        """
        Tests if clicking on logo returns to index (before logging in)
        """
        elem = self.driver.find_element_by_id('navbar_login')
        elem.click()
        elem = self.driver.find_element_by_id('navbar_logo')
        elem.click()
        assert "Welcome to Prodigal!" in self.driver.title

    def test_login_success(self):
        """
        Tests login and redirect to profile page after success.
        """
        elem = self.driver.find_element_by_id('navbar_login')
        elem.click()
        elem = self.driver.find_element_by_id('usr')
        elem.send_keys('test')
        elem = self.driver.find_element_by_id('pass')
        elem.send_keys('pw')
        elem = self.driver.find_element_by_id('submit')
        elem.click()
        elem = self.driver.find_element_by_id('profile_email')
        assert elem.text == 'test@gmail.com'

    def test_login_epic_fail(self):
        """
        Tests login with invalid credentials.
        """
        elem = self.driver.find_element_by_id('navbar_login')
        elem.click()
        elem = self.driver.find_element_by_id('usr')
        elem.send_keys('test')
        elem = self.driver.find_element_by_id('pass')
        elem.send_keys('pwd')
        elem = self.driver.find_element_by_id('submit')
        elem.click()
        elem = self.driver.find_element_by_id('login_fail_msg')
        assert elem.text == 'Login Failed!'

    def test_sign_out(self):
        """
        Tests logging out from app.
        """
        elem = self.driver.find_element_by_id('navbar_login')
        elem.click()
        elem = self.driver.find_element_by_id('usr')
        elem.send_keys('test')
        elem = self.driver.find_element_by_id('pass')
        elem.send_keys('pw')
        elem = self.driver.find_element_by_id('submit')
        elem.click()
        elem = self.driver.find_element_by_xpath('/html/body/nav/ul/li[2]/a')
        elem.click()
        self.assertEqual(self.driver.title, 'Welcome to Prodigal!')

    def test_search_bar_on_success(self):
        """
        Tests if search returns right results.
        """
        elem = self.driver.find_element_by_id('navbar_login')
        elem.click()
        elem = self.driver.find_element_by_id('usr')
        elem.send_keys('test')
        elem = self.driver.find_element_by_id('pass')
        elem.send_keys('pw')
        elem = self.driver.find_element_by_id('submit')
        elem.click()
        elem = self.driver.find_element_by_id('navbar_searchbox')
        elem.send_keys('Apple Inc.')
        elem.submit()
        elem = self.driver.find_element_by_id('company_name')
        assert 'Apple' in elem.text
        elem = self.driver.find_element_by_id('company_description')
        assert elem.text
        elem = self.driver.find_element_by_id('news')
        assert elem.text

    def test_search_bar_on_epic_fail(self):
        """
        Tests searching for non-existing company.
        """
        elem = self.driver.find_element_by_id('navbar_login')
        elem.click()
        elem = self.driver.find_element_by_id('usr')
        elem.send_keys('test')
        elem = self.driver.find_element_by_id('pass')
        elem.send_keys('pw')
        elem = self.driver.find_element_by_id('submit')
        elem.click()
        elem = self.driver.find_element_by_id('navbar_searchbox')
        elem.send_keys('xyz')
        elem.submit()
        elem = self.driver.find_element_by_id('fail')
        assert elem.text

    def test_profile_page_history(self):
        """
        Tests if search history is properly updated.
        """
        elem = self.driver.find_element_by_id('navbar_login')
        elem.click()
        elem = self.driver.find_element_by_id('usr')
        elem.send_keys('test')
        elem = self.driver.find_element_by_id('pass')
        elem.send_keys('pw')
        elem = self.driver.find_element_by_id('submit')
        elem.click()
        elem = self.driver.find_element_by_id('navbar_searchbox')
        elem.send_keys('Adobe Systems Incorporated')
        elem.submit()
        elem = self.driver.find_element_by_id('navbar_logo')
        elem.click()
        elem = self.driver.find_element_by_id('ADBE')
        assert elem.get_attribute("value") == 'Adobe Systems Incorporated'

    def test_search_sector(self):
        """
        Tests reaching search by sector page.
        """
        elem = self.driver.find_element_by_id('navbar_login')
        elem.click()
        elem = self.driver.find_element_by_id('usr')
        elem.send_keys('test')
        elem = self.driver.find_element_by_id('pass')
        elem.send_keys('pw')
        elem = self.driver.find_element_by_id('submit')
        elem.click()
        elem = self.driver.find_element_by_id('sector_dropdown')
        elem.click()
        elem = self.driver.find_element_by_id('Basic Industries')
        elem.click()
        elem = self.driver.find_elements_by_class_name('list-group-item')
        self.assertTrue(len(elem) > 0)

    def tearDown(self):
        self.driver.quit()


class CodeStyleTestCase(TestCase):

    def test_pep8(self):
        """
        Tests if files in test_files are PEP8 compliant.
        """
        pep = pycodestyle.StyleGuide()
        test_files = ['prodigal_app/views.py', 'prodigal_app/models.py',
                      'prodigal_app/tests.py', 'prodigal_app/test_backend.py',
                      'prodigal_app/urls.py', 'prodigal_app/nasdaq_scraper.py',
                      ]
        result = pep.check_files(test_files)
        self.assertEqual(result.total_errors, 0)
