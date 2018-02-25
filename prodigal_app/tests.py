from django.test import TestCase

# Create your tests here.
import unittest
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class TestSignup(unittest.TestCase):

    def setUp(self):
        opts = FirefoxOptions()
        opts.add_argument("--headless")
        firefox_capabilities = DesiredCapabilities.FIREFOX
        firefox_capabilities['marionette'] = True
        firefox_capabilities['binary'] = '/usr/bin/firefox'
        self.driver = webdriver.Firefox(capabilities=firefox_capabilities, firefox_options=opts)

    def test_homepage_rendering(self):
        self.driver.get("https://prodigal-beta.azurewebsites.net/")
        assert "Welcome to Prodigal!" in self.driver.title

    def test_logo_return_to_homepage(self):
        self.driver.get("https://prodigal-beta.azurewebsites.net/")
        elem = self.driver.find_element_by_id('navbar_login')
        elem.click()
        elem = self.driver.find_element_by_id('navbar_logo')
        elem.click()
        assert "Welcome to Prodigal!" in self.driver.title

    def tearDown(self):
        self.driver.quit


if __name__ == '__main__':
    unittest.main()