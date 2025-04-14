from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
import logging
import base64
from PIL import Image
from io import BytesIO

# Set up logging
logging.basicConfig(level=logging.INFO)

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    return webdriver.Chrome(options=chrome_options)

def get_qr_code(driver):
    try:
        # Wait for page to load completely
        time.sleep(5)
        
        # Try multiple selectors for QR code
        selectors = [
            "//canvas[@aria-label='Scan me!']",
            "//div[contains(@class, '_19vUU')]//canvas",
            "//canvas[contains(@aria-label, 'QR')]",
            "//canvas"
        ]
        
        qr_element = None
        for selector in selectors:
            try:
                qr_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                if qr_element.is_displayed():
                    break
            except:
                continue
                
        if not qr_element:
            raise Exception("QR code element not found")

        # Take screenshot of the entire page
        screenshot = driver.get_screenshot_as_png()
        screenshot_image = Image.open(BytesIO(screenshot))
        
        # Get QR code location
        location = qr_element.location
        size = qr_element.size
        
        # Calculate QR code coordinates
        left = location['x']
        top = location['y']
        right = location['x'] + size['width']
        bottom = location['y'] + size['height']
        
        # Crop QR code from screenshot
        qr_image = screenshot_image.crop((left, top, right, bottom))
        
        # Save QR code
        qr_image.save("whatsapp_qr.png")
        logging.info("QR code saved as 'whatsapp_qr.png'")
        
        # Also save full screenshot for debugging
        screenshot_image.save("full_screenshot.png")
        logging.info("Full screenshot saved as 'full_screenshot.png'")
        
        # Wait for user to press Enter
        input("\nQR code has been saved. Scan it with WhatsApp and press Enter to continue...")
        
        return True
        
    except Exception as e:
        logging.error(f"Failed to get QR code: {str(e)}")
        # Save page source for debugging
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        logging.info("Page source saved as 'page_source.html'")
        return False

def wait_for_login(driver):
    try:
        logging.info("Checking for successful login...")
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, '//div[@id="pane-side"]'))
        )
        logging.info("Login successful!")
        return True
    except Exception as e:
        logging.error(f"Login timeout: {str(e)}")
        return False

def send_message(driver, phone_number, message):
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
    # try:
    #     logging.info(f"Opening chat for phone number {phone_number}")
    #     driver.get(f"https://web.whatsapp.com/send?phone={phone_number}")

    #     logging.info("Waiting for chat to load...")
    #     message_box = WebDriverWait(driver, 30).until(
    #         EC.presence_of_element_located((By.XPATH, '//div[@role="textbox"]'))
    #     )

    #     message_box.click()
    #     message_box.send_keys(message + Keys.ENTER)
    #     logging.info("Message sent successfully!")
    #     return True
    # except Exception as e:
    #     logging.error(f"Failed to send message: {str(e)}")
    #     return False

def main():
    phone_number = "+27619722887"
    message = "Hello from Python!"
    
    driver = setup_driver()
    try:
        logging.info("Starting WhatsApp Web automation...")
        driver.get("https://web.whatsapp.com/")
        logging.info("Loading WhatsApp Web...")
        
        if not get_qr_code(driver):
            return
        
        if not wait_for_login(driver):
            return
            
        send_message(driver, phone_number, message)
        
        time.sleep(3)  # Wait for message to be sent
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()