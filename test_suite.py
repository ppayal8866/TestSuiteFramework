from cgitb import text
from pydoc import describe
from re import A
from xml.dom.minidom import Element
from xml.etree.ElementPath import find
import pytest
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType


# Factory Method Pattern: Create a factory function to instantiate the WebDriver instance
def create_driver(browser_name):
    if browser_name == 'firefox':
        return webdriver.Firefox()
    elif browser_name == 'chrome':
        return webdriver.Chrome()
    else:
        raise ValueError(f'Unsupported browser: {browser_name}')


# Singleton Pattern: Create a singleton class to manage the WebDriver instance
class DriverManager:
    _instance = None

    @classmethod
    def get_instance(cls, browser_name):
        if not cls._instance:
            cls._instance = create_driver(browser_name)
        return cls._instance


# Page Object Pattern: Create a class to represent the OpenAI homepage
class HomePage:
    BASE_URL = 'https://www.google.com/'

    def __init__(self, driver):
        self.driver = driver

    def open(self):
        self.driver.get(self.BASE_URL)

    def get_title(self):
        return self.driver.title
    
    def click_about_link(self):
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'About'))
        )
        element.click()
        time.sleep(2)

    def get_current_url(self):
        return self.driver.current_url

class AboutPage:
    BASE_URL = "https://about.google/?fg=1&utm_source=google-US&utm_medium=referral&utm_campaign=hp-header/"
    
    def __init__(self, driver):
        self.driver = driver

    def open(self):
        self.driver.get(self.BASE_URL)

    def get_title(self):
        return self.driver.title

    def get_header_text(self):
        return self.driver.find_element(By.CSS_SELECTOR, 'h1').text
    
    def get_learn_more_button(self):
        return self.driver.find_element(By.PARTIAL_LINK_TEXT, 'Learn more')
        
    def click_careers_link(self):
        # element = self.driver.find_element(By.PARTIAL_LINK_TEXT, 'Careers')
        # element.click()
        # time.sleep(2)
        # windows = self.driver.window_handles
        # self.driver.switch_to.window(windows[1])
        element = self.driver.find_element(By.PARTIAL_LINK_TEXT, 'Careers')
        href = element.get_attribute("href")
        self.driver.execute_script("window.location.href = arguments[0];", href)
        time.sleep(2)
        # element = WebDriverWait(self.driver, 10).until(
        #     EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'careers.google.com'))
        # )
        # element.click()
          
    def get_current_url(self):
        return self.driver.current_url
        
class CareersPage:
    BASE_URL = "https://careers.google.com/?utm_source=about&utm_medium=referral&utm_campaign=footer-link"
    
    def __init__(self, driver):
        self.driver = driver
        
    def open(self):
        self.driver.get(self.BASE_URL)
    def get_title(self):
        return self.driver.title

    def get_header_text(self):
        return self.driver.find_element(By.CSS_SELECTOR, 'h1').text

    def click_job_listing(self):
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'Jobs'))
        )
        element.click()

    def get_current_url(self):
        return self.driver.current_url


@pytest.fixture(scope='module')
def driver():
    chrome_service = Service(ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install())

    chrome_options = Options()
    options = [
    "--headless",
    "--disable-gpu",
    "--window-size=1920,1200",
    "--ignore-certificate-errors",
    "--disable-extensions",
    "--no-sandbox",
    "--disable-dev-shm-usage"
]
    for option in options:
        chrome_options.add_argument(option)

    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    yield driver
    driver.quit()


# 1. Define a fixture to set up the WebDriver instance
# @pytest.fixture(scope='module')
def gui_driver():
    # Create the WebDriver instance using the DriverManager
    driver_manager = DriverManager.get_instance('firefox')

    # Set up the driver options (e.g., maximize window, set implicit wait time)
    driver_manager.maximize_window()
    driver_manager.implicitly_wait(10)

    # Pass the driver instance to the tests
    yield driver_manager

    # Teardown - quit the WebDriver instance after the tests complete
    driver_manager.quit()


# 2. Write test functions using the driver fixture to perform actions and assertions on the website
def test_home_page_title(driver):
    homepage = HomePage(driver)
    homepage.open()
    
    assert 'Google' in homepage.get_title()
    assert driver.find_element(By.NAME, 'q').is_displayed(), "Search input field is not displayed on the homepage"
    assert driver.find_element(By.CLASS_NAME, 'gNO89b'), "Google Search button is not displayed on the homepage"
    assert driver.find_element(By.ID, 'gbqfbb'), "I'm Feeling Lucky button is not displayed on the homepage"
    assert driver.find_element(By.CLASS_NAME,'pHiOh'), "Advertising is not displyed on homepage footer"


def test_home_page_navigation(driver):
    homepage = HomePage(driver)
    homepage.open()
    homepage.click_about_link()
    current_url = homepage.get_current_url()
    expected_url = 'https://about.google/?fg=1&utm_source=google-US&utm_medium=referral&utm_campaign=hp-header'
    assert current_url == expected_url, f"Expected URL: {expected_url}, Actual URL: {current_url}"

  
def test_about_page(driver):
    aboutpage = AboutPage(driver)
    aboutpage.open()
    assert aboutpage.get_title() == "Google - About Google, Our Culture & Company News"
    assert "Our mission is to" in aboutpage.get_header_text()
    assert aboutpage.get_learn_more_button().get_attribute("href") == "https://bard.google.com/"


def test_about_page_navigation(driver):
    aboutpage = AboutPage(driver)
    aboutpage.open() 
    aboutpage.click_careers_link()
    current_url = aboutpage.get_current_url()
    expected_url = 'https://careers.google.com/?utm_campaign=footer-link&utm_medium=referral&utm_source=about'
    assert aboutpage.get_title() == "Build for everyone - Google Careers"
    assert current_url == expected_url, f"Expected URL: {expected_url}, Actual URL: {current_url}"


def test_careers_page(driver):
    careerspage = CareersPage(driver)
    careerspage.open()
    assert careerspage.get_title() == "Build for everyone - Google Careers"
    assert "for everyone" in careerspage.get_header_text()


def test_careers_page_navigation(driver):
    careerspage = CareersPage(driver)
    careerspage.open()
    careerspage.click_job_listing()
    current_url = careerspage.get_current_url()
    expected_url = 'https://www.google.com/about/careers/applications/jobs/results/?utm_campaign=footer-link&utm_medium=referral&utm_source=about'
    assert careerspage.get_title() == "Search Jobs — Google Careers"
    assert current_url == expected_url, f"Expected URL: {expected_url}, Actual URL: {current_url}"
   

if __name__ == '__main__':
    pytest.main(['-v'])
