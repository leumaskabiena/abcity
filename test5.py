from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Configure Chrome options for headless mode
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")

# Start Chrome WebDriver
driver = webdriver.Chrome(options=options)
driver.get("https://web.whatsapp.com/")

try:
    # Wait for QR code to load and capture
    logging.info("Waiting for QR code to load...")
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '//canvas'))
    )
    
    # Capture and save QR code screenshot
    driver.save_screenshot('whatsapp_qr.png')
    logging.info("QR code screenshot saved as 'whatsapp_qr.png'")
    input("Scan the QR code from the screenshot and press Enter to continue...")

    phone_number = "+27619722887"
    message = "Hello from Python!"

    # Open chat using direct URL
    logging.info("Opening chat for phone number %s", phone_number)
    driver.get(f"https://web.whatsapp.com/send?phone={phone_number}")

    # Wait for chat to load
    logging.info("Waiting for chat to load...")
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '//div[@role="textbox"]'))
    )

    # Find message input boxes
    logging.info("Locating message input boxes...")
    message_boxes = WebDriverWait(driver, 30).until(
        EC.presence_of_all_elements_located((By.XPATH, '//div[@role="textbox"]'))
    )

    logging.info("Found %d text boxes", len(message_boxes))

    if len(message_boxes) < 2:
        logging.error("Insufficient text boxes found")
        raise Exception("Required text boxes not found")

    # Select and interact with second text box
    second_message_box = message_boxes[1]
    second_message_box.click()
    second_message_box.send_keys(message + Keys.ENTER)
    logging.info("Message sent successfully!")

    # Final confirmation screenshot
    driver.save_screenshot('message_sent_confirmation.png')
    logging.info("Confirmation screenshot saved")

except Exception as e:
    logging.error("Error occurred: %s", str(e))
    driver.save_screenshot('error_screenshot.png')
    logging.error("Error screenshot saved")

finally:
    driver.quit()