from django.test import TestCase

# Create your tests here.
import unittest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class TestSignup(unittest.TestCase):

    def setUp(self):
        chrome_opts = Options()
        chrome_opts.add_argument("--disable-extensions")
        chrome_opts.add_argument("--headless")
        chrome_opts.add_argument("--no-sandbox")
        chrome_opts.add_argument("--disable-gpu")
        self.driver = webdriver.Chrome(options=chrome_opts)
        self.driver.get("https://prodigal-gamma.azurewebsites.net/")
        #  self.driver.get("http://0.0.0.0:8000/")

    def test_homepage_rendering(self):
        assert "Welcome to Prodigal!" in self.driver.title

    def test_logo_return_to_homepage(self):
        elem = self.driver.find_element_by_id('navbar_login')
        elem.click()
        elem = self.driver.find_element_by_id('navbar_logo')
        elem.click()
        assert "Welcome to Prodigal!" in self.driver.title
    
    def test_login_success(self):
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
    
    def test_search_bar_on_success(self):
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

    def tearDown(self):
        self.driver.quit


if __name__ == '__main__':
    unittest.main()
