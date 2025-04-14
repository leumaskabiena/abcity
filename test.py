# Email Sending Utility
import smtplib
import pywhatkit
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(sender_email, sender_password, recipient_email, subject, message):
    """
    Send an email using Gmail SMTP server.
    
    Note: For Gmail, you need to:
    1. Enable 2-factor authentication
    2. Generate an App Password
    3. Use the App Password instead of your regular password
    """
    try:
        # Set up the MIME
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Add body to email
        msg.attach(MIMEText(message, 'plain'))

        # Create SMTP session
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        # Login to the server
        server.login(sender_email, sender_password)
        
        # Send email
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        
        # Close session
        server.quit()
        print("Email sent successfully!")
        
    except Exception as e:
        print(f"Error sending email: {str(e)}")

# WhatsApp Web Messaging Utility
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def send_whatsapp_message(phone_number, message):
    """
    Send a WhatsApp message using WhatsApp Web.
    Phone number should be in international format without '+' (e.g., '1234567890')
    """
    try:
        # Initialize the driver
        driver = webdriver.Chrome()
        
        # Construct WhatsApp Web URL with phone number
        url = f"https://web.whatsapp.com/send?phone={phone_number}&text={message}"
        driver.get(url)
        
        # Wait for the page to load and QR code to be scanned
        print("Please scan the QR code within 30 seconds...")
        
        # Wait for the message input box to be present
        send_button = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//button[@data-testid='compose-btn-send']"))
        )
        
        # Click the send button
        send_button.click()
        
        # Wait a moment for the message to be sent
        time.sleep(2)
        
        # Close the browser
        driver.quit()
        print("WhatsApp message sent successfully!")
        
    except Exception as e:
        print(f"Error sending WhatsApp message: {str(e)}")
        if 'driver' in locals():
            driver.quit()

# Example usage
if __name__ == "__main__":
    # Email example
    email_config = {
        "sender_email": "leumaskabiena@gmail.com",
        "sender_password": "cnjr kvkt slys lhlv",
        "recipient_email": "smkabiena@outlook.com",
        "subject": "Test Email",
        "message": "Hello! This is a test email sent from Python."
    }
    
    # Send email
    send_email(**email_config)
    
    # WhatsApp example
    whatsapp_config = {
        "phone_number": "0619722887",  # Without country code
        "message": "Hello! This is a test message sent from Python."
    }
    
    # Send WhatsApp message
    send_whatsapp_message(**whatsapp_config)