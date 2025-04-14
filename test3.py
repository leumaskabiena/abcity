from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Start Chrome WebDriver
driver = webdriver.Chrome()
driver.get("https://web.whatsapp.com/")
input("Scan QR code and press Enter (ensure you're logged in)...")

phone_number = "+27619722887"
message = "Hello from Python!"

try:
    # Open chat using direct URL
    logging.info("Opening chat for phone number %s", phone_number)
    driver.get(f"https://web.whatsapp.com/send?phone={phone_number}")
    
    # Explicitly wait for the chat to load
    logging.info("Waiting for chat to load...")
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '//div[@role="textbox"]'))
    )
    
    # Wait until the message box is interactable
    logging.info("Finding message input box...")
    message_box = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '//div[@role="textbox"]'))
    )
    
    # Type message and send
    logging.info("Typing and sending message...")
    message_box.send_keys(message + Keys.ENTER)
    
    logging.info("Message sent successfully!")
    time.sleep(3)

except Exception as e:
    logging.error("Failed to send message: %s", str(e))

finally:
    driver.quit()
