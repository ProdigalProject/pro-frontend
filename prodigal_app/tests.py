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
        # firefox_capabilities = DesiredCapabilities.FIREFOX
        # firefox_capabilities['marionette'] = True
        # firefox_capabilities['binary'] = '/usr/bin/firefox'
          self.driver = webdriver.Chrome(options=chrome_opts)
          self.driver.get("https://prodigal-gamma.azurewebsites.net/")
          #self.driver.get("http://0.0.0.0:8000/")

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
        #elem = self.driver.find_element_by_xpath("//a[contains(text(),'Secret backdoor to profile page')]")
        elem.click()
        elem = self.driver.find_element_by_id('usr')
        elem.send_keys('test')

        elem = self.driver.find_element_by_id('pass')
        elem.send_keys('pw')
        
        elem = self.driver.find_element_by_id('submit')
        elem.click() 
        
        elem = self.driver.find_element_by_id('profile_username')
        assert elem.text == 'test'
        
    def test_login_epic_fail(self):
        elem = self.driver.find_element_by_id('navbar_login')
        #elem = self.driver.find_element_by_xpath("//a[contains(text(),'Secret backdoor to profile page')]")
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
        #elem = self.driver.find_element_by_xpath("//a[contains(text(),'Secret backdoor to profile page')]")
        elem.click()
        elem = self.driver.find_element_by_id('usr')
        elem.send_keys('test')

        elem = self.driver.find_element_by_id('pass')
        elem.send_keys('pw')
        
        elem = self.driver.find_element_by_id('submit')
        elem.click() 
        
        elem = self.driver.find_element_by_id('navbar_searchbox')
        elem.send_keys('aapl')
        elem.submit()
        
        
        elem = self.driver.find_element_by_id('company_name')
        assert elem.text == 'Apple Inc.'
        elem = self.driver.find_element_by_id('company_description')
        assert elem.text
        elem = self.driver.find_element_by_id('news')
        assert elem.text
        
        
        # test exception handle

        # test api status
    
    def test_search_bar_on_epic_fail(self):
        elem = self.driver.find_element_by_id('navbar_login')
        #elem = self.driver.find_element_by_xpath("//a[contains(text(),'Secret backdoor to profile page')]")
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
        assert elem.text == 'No Matching Result.'

    def tearDown(self):
        self.driver.quit


if __name__ == '__main__':
    unittest.main()
