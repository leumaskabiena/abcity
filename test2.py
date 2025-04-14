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

    # Locate all elements that are message input boxes
    logging.info("Finding all message input boxes...")
    message_boxes = WebDriverWait(driver, 30).until(
        EC.presence_of_all_elements_located((By.XPATH, '//div[@role="textbox"]'))
    )

    # Print the count of matching elements
    logging.info("Number of text boxes found: %d", len(message_boxes))

    if len(message_boxes) < 2:
        logging.error("Less than two message input boxes found. Exiting.")
        driver.quit()
        exit()

    # Select the second text box (index 1)
    second_message_box = message_boxes[1]
    logging.info("Sending message to the second text box...")

    # Click the message box to ensure it is focused
    second_message_box.click()

    # Type message and send
    second_message_box.send_keys(message + Keys.ENTER)
    logging.info("Message sent successfully!")

    time.sleep(3)

except Exception as e:
    logging.error("Failed to send message: %s", str(e))

finally:
    driver.quit()
