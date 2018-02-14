from django.test import TestCase

# Create your tests here.
import unittest
from selenium import webdriver

class TestSignup(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox()

    def test_signup_fire(self):
        self.driver.get("https://prodigal-beta.azurewebsites.net/")
        assert "Welcome to Prodigal!" in driver.title
        '''
        self.driver.find_element_by_id('title'). ("Welcome to Prodigal!")
        self.driver.find_element_by_id('id_body').send_keys("test body")
        self.driver.find_element_by_id('submit').click()
        self.assertIn("http://localhost:8000/", self.driver.current_url)
		'''
    def tearDown(self):
        self.driver.quit

if __name__ == '__main__':
    unittest.main()