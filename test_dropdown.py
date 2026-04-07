import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select

class TestDropdown:
    def setup_method(self):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.driver.maximize_window()

    def teardown_method(self):
        self.driver.quit()

    # Verify that the default selection is correct
    def test_default_selection(self):
        self.driver.get("https://the-internet.herokuapp.com/dropdown")
        dropdown = Select(self.driver.find_element(By.ID, "dropdown"))
        time.sleep(1)
        assert dropdown.first_selected_option.text == "Please select an option"

    # Verify that selecting option 1 works correctly
    def test_select_option(self):
        self.driver.get("https://the-internet.herokuapp.com/dropdown")
        dropdown = Select(self.driver.find_element(By.ID, "dropdown"))
        time.sleep(1)
        dropdown.select_by_visible_text("Option 1")
        assert dropdown.first_selected_option.text == "Option 1"

    # Verify that selecting option 2 works correctly
    def test_select_option_2(self):
        self.driver.get("https://the-internet.herokuapp.com/dropdown")
        dropdown = Select(self.driver.find_element(By.ID, "dropdown"))
        time.sleep(1)
        dropdown.select_by_visible_text("Option 2")
        assert dropdown.first_selected_option.text == "Option 2"
    
    # Verify that selecting an option by value works correctly
    def test_select_by_value(self):
        self.driver.get("https://the-internet.herokuapp.com/dropdown")
        dropdown = Select(self.driver.find_element(By.ID, "dropdown"))
        dropdown.select_by_value("1")

        assert dropdown.first_selected_option.text == "Option 1"

    # Verify that changing the selection updates the selected option correctly
    def test_change_selection(self):
        self.driver.get("https://the-internet.herokuapp.com/dropdown")
        dropdown = Select(self.driver.find_element(By.ID, "dropdown"))
        time.sleep(1)
        dropdown.select_by_visible_text("Option 1")
        time.sleep(1)
        dropdown.select_by_visible_text("Option 2")

        assert dropdown.first_selected_option.text == "Option 2"
    
    # Verify that the dropdown contains the expected number of options
    def test_dropdown_options_count(self):
        self.driver.get("https://the-internet.herokuapp.com/dropdown")
        dropdown = Select(self.driver.find_element(By.ID, "dropdown"))
        options = dropdown.options

        assert len(options) == 3