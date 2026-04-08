import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

BASE_URL = "https://www.saucedemo.com/"
VALID_USERNAME = "standard_user"
VALID_PASSWORD = "secret_sauce"

class TestSwagLabsSystem:
    def setup_method(self):
    # To prevent Chrome's password manager from interfering with our tests, we can disable it using ChromeOptions
        options = Options()
        prefs = {
            "profile.password_manager_leak_detection": False,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False
        }
        options.add_experimental_option("prefs", prefs)

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.driver.maximize_window()
    
    # Helper method to perform login 
    def login(self, username, password):
        self.driver.get(BASE_URL)
        self.driver.find_element(By.ID, "user-name").send_keys(username)
        self.driver.find_element(By.ID, "password").send_keys(password)
        self.driver.find_element(By.ID, "login-button").click()
    
    # Helper method to add an item to the cart and navigate to the cart page (used mainly in checkout tests)
    def add_item_to_cart(self):
        self.login(VALID_USERNAME, VALID_PASSWORD)
        self.driver.find_element(By.CSS_SELECTOR, ".inventory_item:first-child button").click()
        self.driver.find_element(By.CSS_SELECTOR, ".shopping_cart_link").click()
        WebDriverWait(self.driver, 10).until(EC.url_contains("cart.html"))

    def teardown_method(self):
        self.driver.quit()

    # ------- Login Tests -------

    # Verify that valid credentials log the user in successfully
    def test_valid_login(self):
        self.login(VALID_USERNAME, VALID_PASSWORD)
        WebDriverWait(self.driver, 10).until(EC.url_contains("inventory.html"))
        assert "inventory.html" in self.driver.current_url

    def test_invalid_username(self):
        """Verify that an invalid username shows an error message."""
        self.login("wrong_user", VALID_PASSWORD)
        error = self.driver.find_element(By.CSS_SELECTOR, "[data-test='error']")
        assert "Username and password do not match" in error.text

    def test_invalid_password(self):
        """Verify that an invalid password shows an error message."""
        self.login(VALID_USERNAME, "wrong_password")
        error = self.driver.find_element(By.CSS_SELECTOR, "[data-test='error']")
        assert "Username and password do not match" in error.text

    def test_locked_out_user(self):
        """Verify that a locked out user cannot log in."""
        self.login("locked_out_user", VALID_PASSWORD)
        self.driver.find_element(By.ID, "login-button").click()
        error = self.driver.find_element(By.CSS_SELECTOR, "[data-test='error']")
        assert "Sorry, this user has been locked out" in error.text

    # ------- Inventory Tests -------

    # Verify that the inventory page displays the correct number of products
    def test_inventory_has_six_products(self):
        self.login(VALID_USERNAME, VALID_PASSWORD)
        products = self.driver.find_elements(By.CSS_SELECTOR, ".inventory_item")
        assert len(products) == 6

    # Verify that all products have names displayed
    def test_products_have_names(self):
        self.login(VALID_USERNAME, VALID_PASSWORD)
        names = self.driver.find_elements(By.CSS_SELECTOR, ".inventory_item_name")
        for name in names:
            assert name.text != ""

    # Verify that all products have prices displayed
    def test_products_have_prices(self):
        self.login(VALID_USERNAME, VALID_PASSWORD)
        prices = self.driver.find_elements(By.CSS_SELECTOR, ".inventory_item_price")

        for price in prices:
            assert "$" in price.text
            price_value = price.text.replace("$", "")
            float_price = float(price_value)
            assert float_price > 0

    # Verify that sorting by price low to high works correctly
    def test_sort_by_price_low_to_high(self):
        self.login(VALID_USERNAME, VALID_PASSWORD)
        select = Select(self.driver.find_element(By.CSS_SELECTOR, ".product_sort_container"))
        select.select_by_value("lohi")
        prices = self.driver.find_elements(By.CSS_SELECTOR, ".inventory_item_price")
        price_values = [float(p.text.replace("$", "")) for p in prices]
        assert price_values == sorted(price_values)

    # Verify that sorting by price high to low works correctly
    def test_sort_by_price_high_to_low(self):
        self.login(VALID_USERNAME, VALID_PASSWORD)
        select = Select(self.driver.find_element(By.CSS_SELECTOR, ".product_sort_container"))
        select.select_by_value("hilo")
        prices = self.driver.find_elements(By.CSS_SELECTOR, ".inventory_item_price")
        price_values = [float(p.text.replace("$", "")) for p in prices]
        assert price_values == sorted(price_values, reverse=True)

    # Verify that sorting by name A to Z works correctly
    def test_sort_by_name_a_to_z(self):
        self.login(VALID_USERNAME, VALID_PASSWORD)
        select = Select(self.driver.find_element(By.CSS_SELECTOR, ".product_sort_container"))
        select.select_by_value("az")
        names = self.driver.find_elements(By.CSS_SELECTOR, ".inventory_item_name")
        name_values = [n.text for n in names]
        assert name_values == sorted(name_values)

    # Verify that sorting by name Z to A works correctly
    def test_sort_by_name_z_to_a(self):
        self.login(VALID_USERNAME, VALID_PASSWORD)
        select = Select(self.driver.find_element(By.CSS_SELECTOR, ".product_sort_container"))
        select.select_by_value("za")
        names = self.driver.find_elements(By.CSS_SELECTOR, ".inventory_item_name")
        name_values = [n.text for n in names]
        assert name_values == sorted(name_values, reverse=True)
    
    # ------- Shopping Cart Tests -------

    # Verify that adding a single item updates the cart count
    def test_add_single_item_to_cart(self):
        self.login(VALID_USERNAME, VALID_PASSWORD)
        self.driver.find_element(By.CSS_SELECTOR, ".inventory_item:first-child button").click()
        cart_count = self.driver.find_element(By.CSS_SELECTOR, ".shopping_cart_badge")
        assert cart_count.text == "1"

    # Verify that adding multiple items updates the cart count correctly
    def test_add_multiple_items_to_cart(self):
        """Verify that adding multiple items updates the cart count correctly."""
        self.login(VALID_USERNAME, VALID_PASSWORD)
        buttons = self.driver.find_elements(By.CSS_SELECTOR, ".btn_inventory")
        buttons[0].click()
        buttons[1].click()
        buttons[2].click()
        cart_count = self.driver.find_element(By.CSS_SELECTOR, ".shopping_cart_badge")
        assert cart_count.text == "3"

    # Verify that adding and removing the same item updates the cart count correctly
    def test_remove_item_from_inventory(self):    
        self.login(VALID_USERNAME, VALID_PASSWORD)
        # Add the first item to the cart
        self.driver.find_element(By.CSS_SELECTOR, ".inventory_item:first-child button").click()
        num_items_in_cart = self.driver.find_elements(By.CSS_SELECTOR, ".shopping_cart_badge")
        assert len(num_items_in_cart) == 1

        # Since the "Remove" button replaces the "Add to cart" button, we can click it again to remove the item
        self.driver.find_element(By.CSS_SELECTOR, ".inventory_item:first-child button").click()
        updated_num_items_in_cart = self.driver.find_elements(By.CSS_SELECTOR, ".shopping_cart_badge")
        assert len(updated_num_items_in_cart) == 0

    # Verify that the shopping cart page displays the correct items after adding them
    def test_cart_displays_added_items(self):
        self.login(VALID_USERNAME, VALID_PASSWORD)
        self.driver.find_element(By.CSS_SELECTOR, ".inventory_item:first-child button").click()

        # Click the shopping cart icon to navigate to the shopping cart page
        self.driver.find_element(By.CSS_SELECTOR, ".shopping_cart_link").click()
        WebDriverWait(self.driver, 10).until(EC.url_contains("cart.html"))
        cart_items = self.driver.find_elements(By.CSS_SELECTOR, ".cart_item")
        assert len(cart_items) == 1

    # Verify that removing an item from the shopping cart page works correctly
    def test_remove_item_from_cart(self):
        self.login(VALID_USERNAME, VALID_PASSWORD)
        self.driver.find_element(By.CSS_SELECTOR, ".inventory_item:first-child button").click()
        self.driver.find_element(By.CSS_SELECTOR, ".shopping_cart_link").click()
        WebDriverWait(self.driver, 10).until(EC.url_contains("cart.html"))
        self.driver.find_element(By.CSS_SELECTOR, ".cart_item button").click()
        cart_items = self.driver.find_elements(By.CSS_SELECTOR, ".cart_item")
        assert len(cart_items) == 0

    # Verify that clicking "Continue Shopping" from the cart page returns the user to the inventory page
    def test_continue_shopping_from_cart(self):
        self.add_item_to_cart()
        WebDriverWait(self.driver, 10).until(EC.url_contains("cart.html"))
        self.driver.find_element(By.ID, "continue-shopping").click()
        WebDriverWait(self.driver, 10).until(EC.url_contains("inventory.html"))
        assert "inventory.html" in self.driver.current_url

    # ------- Checkout Step 1 Tests -------

    # Verify that the checkout button is present on the shopping cart page after adding an item
    def test_checkout_button_present(self):
        self.add_item_to_cart()
        assert self.driver.find_element(By.ID, "checkout").is_displayed()

    # Verify that clicking the checkout button navigates to the checkout form
    def test_navigate_to_checkout(self):
        self.add_item_to_cart()
        self.driver.find_element(By.ID, "checkout").click()
        WebDriverWait(self.driver, 10).until(EC.url_contains("checkout-step-one.html"))
        assert "checkout-step-one.html" in self.driver.current_url

    # Verify that checkout brings the user to the second step of the checkout process when valid information is entered
    def test_checkout_with_valid_information(self):
        self.add_item_to_cart()
        self.driver.find_element(By.ID, "checkout").click()
        self.driver.find_element(By.ID, "first-name").send_keys("John")
        self.driver.find_element(By.ID, "last-name").send_keys("Doe")
        self.driver.find_element(By.ID, "postal-code").send_keys("12345")

        #Clicking continue takes the user to the second step of the checkout process where they can review their order
        self.driver.find_element(By.ID, "continue").click()

        WebDriverWait(self.driver, 10).until(EC.url_contains("checkout-step-two.html"))
        assert "checkout-step-two.html" in self.driver.current_url

    # Verify that the checkout form shows an error message when required fields are missing
    def test_checkout_missing_first_name(self):
        self.add_item_to_cart()
        self.driver.find_element(By.ID, "checkout").click()
        self.driver.find_element(By.ID, "last-name").send_keys("Doe")
        self.driver.find_element(By.ID, "postal-code").send_keys("12345")
        self.driver.find_element(By.ID, "continue").click()
        error = self.driver.find_element(By.CSS_SELECTOR, "[data-test='error']")
        assert "First Name is required" in error.text

    # Verify that the checkout form shows an error message when the last name is missing
    def test_checkout_missing_last_name(self):
        self.add_item_to_cart()
        self.driver.find_element(By.ID, "checkout").click()
        self.driver.find_element(By.ID, "first-name").send_keys("John")
        self.driver.find_element(By.ID, "postal-code").send_keys("12345")
        self.driver.find_element(By.ID, "continue").click()
        error = self.driver.find_element(By.CSS_SELECTOR, "[data-test='error']")
        assert "Last Name is required" in error.text

    # Verify that the checkout form shows an error message when the postal code is missing
    def test_checkout_missing_postal_code(self):
        self.add_item_to_cart()
        self.driver.find_element(By.ID, "checkout").click()
        self.driver.find_element(By.ID, "first-name").send_keys("John")
        self.driver.find_element(By.ID, "last-name").send_keys("Doe")
        self.driver.find_element(By.ID, "continue").click()
        error = self.driver.find_element(By.CSS_SELECTOR, "[data-test='error']")
        assert "Postal Code is required" in error.text
    
    # Verify that clicking "Cancel" from the first step of checkout process returns the user to the shopping cart page
    def test_step1_checkout_cancel(self):
        self.add_item_to_cart()
        self.driver.find_element(By.ID, "checkout").click()
        WebDriverWait(self.driver, 10).until(EC.url_contains("checkout-step-one.html"))
        self.driver.find_element(By.ID, "cancel").click()
        WebDriverWait(self.driver, 10).until(EC.url_contains("cart.html"))
        assert "cart.html" in self.driver.current_url

    # ------- Checkout Step 2 Tests -------

    # Verify that the order summary displays the correct item after proceeding to checkout
    def test_order_summary_displays_item(self):
        self.add_item_to_cart()
        self.driver.find_element(By.ID, "checkout").click()
        self.driver.find_element(By.ID, "first-name").send_keys("John")
        self.driver.find_element(By.ID, "last-name").send_keys("Doe")
        self.driver.find_element(By.ID, "postal-code").send_keys("12345")

        #Clicking continue takes the user to the second step of the checkout process where they can review their order
        self.driver.find_element(By.ID, "continue").click()

        WebDriverWait(self.driver, 10).until(EC.url_contains("checkout-step-two.html"))
        cart_items = self.driver.find_elements(By.CSS_SELECTOR, ".cart_item")
        assert len(cart_items) == 1

    # Verify that the order summary displays a total price after proceeding to stage 2 of checkout
    def test_order_summary_displays_total(self):
        self.add_item_to_cart()
        self.driver.find_element(By.ID, "checkout").click()
        self.driver.find_element(By.ID, "first-name").send_keys("John")
        self.driver.find_element(By.ID, "last-name").send_keys("Doe")
        self.driver.find_element(By.ID, "postal-code").send_keys("12345")
        self.driver.find_element(By.ID, "continue").click()
        WebDriverWait(self.driver, 10).until(EC.url_contains("checkout-step-two.html"))
        total = self.driver.find_element(By.CSS_SELECTOR, ".summary_total_label")
        assert "$" in total.text
        total_value = total.text.replace("Total: $", "")
        float_total = float(total_value)
        assert float_total > 0

    #Verify that clicking "Cancel" from step 2 of the checkout process returns the user to the product page
    def test_order_summary_cancel(self):
        self.add_item_to_cart()
        self.driver.find_element(By.ID, "checkout").click()
        self.driver.find_element(By.ID, "first-name").send_keys("John")
        self.driver.find_element(By.ID, "last-name").send_keys("Doe")
        self.driver.find_element(By.ID, "postal-code").send_keys("12345")
        self.driver.find_element(By.ID, "continue").click()
        self.driver.find_element(By.ID, "cancel").click()
        WebDriverWait(self.driver, 10).until(EC.url_contains("inventory.html"))
        assert "inventory.html" in self.driver.current_url

    # --------- Checkout Complete Tests -------
    # Verify that completing the checkout process shows the order confirmation page
    def test_complete_order(self):
        self.add_item_to_cart()
        self.driver.find_element(By.ID, "checkout").click()
        self.driver.find_element(By.ID, "first-name").send_keys("John")
        self.driver.find_element(By.ID, "last-name").send_keys("Doe")
        self.driver.find_element(By.ID, "postal-code").send_keys("12345")
        self.driver.find_element(By.ID, "continue").click()
     
        # When a user clicks the "Finish" button, they should be taken to the order confirmation page
        self.driver.find_element(By.ID, "finish").click()
        
        WebDriverWait(self.driver, 10).until(EC.url_contains("checkout-complete.html"))

        confirmation = self.driver.find_element(By.CSS_SELECTOR, ".complete-header")
        assert "Thank you for your order!" in confirmation.text

    # Verify that clicking "Back Home" from the order confirmation page returns the user to the inventory page
    def test_back_home_after_order(self):
        self.add_item_to_cart()
        self.driver.find_element(By.ID, "checkout").click()
        self.driver.find_element(By.ID, "first-name").send_keys("John")
        self.driver.find_element(By.ID, "last-name").send_keys("Doe")
        self.driver.find_element(By.ID, "postal-code").send_keys("12345")
        self.driver.find_element(By.ID, "continue").click()
        self.driver.find_element(By.ID, "finish").click()
        self.driver.find_element(By.ID, "back-to-products").click()
        WebDriverWait(self.driver, 10).until(EC.url_contains("inventory.html"))
        assert "inventory.html" in self.driver.current_url

    # ------- Logout Test -------
    # Verify that a logged in user can successfully log out and is redirected to the login page
    def test_logout(self):
        self.login(VALID_USERNAME, VALID_PASSWORD)
        self.driver.find_element(By.ID, "react-burger-menu-btn").click()
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "logout_sidebar_link")))
        self.driver.find_element(By.ID, "logout_sidebar_link").click()
        WebDriverWait(self.driver, 10).until(EC.url_to_be(BASE_URL))
        assert self.driver.current_url == BASE_URL