import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Run using the command: pytest test_suite.py -s
class TestFormAuthentication:
    def setup_method(self):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.driver.maximize_window()

    def teardown_method(self):
        self.driver.quit()

    # Verify that valid credentials log the user in successfully
    def test_valid_login(self):
        self.driver.get("https://the-internet.herokuapp.com/login")
        self.driver.find_element(By.ID, "username").send_keys("tomsmith")
        self.driver.find_element(By.ID, "password").send_keys("SuperSecretPassword!")
        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)
        WebDriverWait(self.driver, 10).until(EC.url_contains("/secure"))
        assert "/secure" in self.driver.current_url, "Failed to login!"

    # Verify that an invalid username shows an error message
    def test_invalid_username(self):
        self.driver.get("https://the-internet.herokuapp.com/login")
        self.driver.find_element(By.ID, "username").send_keys("wronguser")
        self.driver.find_element(By.ID, "password").send_keys("SuperSecretPassword!")
        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)
        error = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, "flash")))
        
        #checks that the error message contains the expected text from the pop up
        assert "Your username is invalid!" in error.text
        
        #Checks that we are still on the login page
        assert "/login" in self.driver.current_url

    # Verify that an invalid password shows an error message
    def test_invalid_password(self):
        self.driver.get("https://the-internet.herokuapp.com/login")
        self.driver.find_element(By.ID, "username").send_keys("tomsmith")
        self.driver.find_element(By.ID, "password").send_keys("wrongpassword")
        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)
        error = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, "flash")))
        assert "Your password is invalid!" in error.text
        assert "/login" in self.driver.current_url

    # Verify that an empty username shows an error message
    def test_empty_username(self):
        self.driver.get("https://the-internet.herokuapp.com/login")
        self.driver.find_element(By.ID, "password").send_keys("SuperSecretPassword!")
        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)
        error = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, "flash")))
        assert "Your username is invalid!" in error.text
        assert "/login" in self.driver.current_url

    # Verify that an empty password shows an error message
    def test_empty_password(self):
        self.driver.get("https://the-internet.herokuapp.com/login")
        self.driver.find_element(By.ID, "username").send_keys("tomsmith")
        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)
        error = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, "flash")))
        assert "Your password is invalid!" in error.text
        assert "/login" in self.driver.current_url

    # Verify that empty credentials show an error message
    def test_empty_credentials(self):
        self.driver.get("https://the-internet.herokuapp.com/login")
        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)
        error = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, "flash")))
        assert "Your username is invalid!" in error.text
        assert "/login" in self.driver.current_url
    
    # Verify that a logged in user can successfully log out
    def test_logout(self):
        self.driver.get("https://the-internet.herokuapp.com/login")
        self.driver.find_element(By.ID, "username").send_keys("tomsmith")
        self.driver.find_element(By.ID, "password").send_keys("SuperSecretPassword!")
        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR, "a[href='/logout']").click()
        time.sleep(1)
        
        logout_message = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, "flash")))
        assert "You logged out of the secure area!" in logout_message.text
        assert "/login" in self.driver.current_url     