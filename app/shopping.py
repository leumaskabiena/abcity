import logging
import time
import datetime
import pickle
import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import re
import urllib.parse
from PIL import Image
from io import BytesIO

from flask import Blueprint, render_template, current_app, jsonify, request, session, redirect, flash, url_for
from google.cloud import firestore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the blueprint
shopping = Blueprint('shopping', __name__)

# Initialize Firestore client
db = firestore.Client()

# Email sending utility
def send_email(sender_email, sender_password, recipient_email, subject, message, is_html=False):
    try:
        # Create message container
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Check if the email should be HTML
        if is_html:
            # Attach HTML message
            msg.attach(MIMEText(message, 'html'))
        else:
            # Attach plain text message
            msg.attach(MIMEText(message, 'plain'))

        # Connect to the SMTP server (e.g., Gmail)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Secure the connection
        server.login(sender_email, sender_password)

        # Send the email
        server.sendmail(sender_email, recipient_email, msg.as_string())

        # Close the server connection
        server.quit()
        
        return True  # Indicate success
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False  # Indicate failure


def get_cart_identifier():
    if 'userId' in session:
        logger.info(f"User identified with userId: {session['userId']}")
        return {'userId': session['userId'], 'cartId': None, 'isGuest': False}
    else:
        if 'cartId' not in session:
            session['cartId'] = str(int(time.time()))  # Generate a cart ID for guest users
            logger.info(f"Generated new cartId for guest: {session['cartId']}")
        else:
            logger.info(f"Using existing cartId for guest: {session['cartId']}")
        return {'userId': None, 'cartId': session['cartId'], 'isGuest': True}

def validate_input(product_id, quantity):
    if not product_id or not quantity:
        raise ValueError('Invalid input, missing: ' + ('productId' if not product_id else 'quantity'))

def get_or_create_cart(user_id, cart_id, is_guest):
    cart_ref = db.collection('carts')
    
    if is_guest:
        cart_query = cart_ref.where('guestId', '==', cart_id)
    else:
        cart_query = cart_ref.where('userId', '==', user_id)
    
    cart_snapshot = cart_query.stream()

    cart_data = None
    cart_doc_id = None  # To store the document ID

    for cart_doc in cart_snapshot:
        cart_data = cart_doc.to_dict()
        cart_doc_id = cart_doc.id  # Capture the document ID
        break

    if not cart_data:
        # Create a new cart if no cart exists
        new_cart_ref = cart_ref.add({
            'guestId' if is_guest else 'userId': cart_id if is_guest else user_id,
            'items': []
        })
        # Return the newly created cart data, including document ID
        cart_data = {
            'id': new_cart_ref.id,  # Document ID
            'items': []
        }
        return cart_data  # Return new cart data

    # Return existing cart data, including document ID
    cart_data['id'] = cart_doc_id
    return cart_data

def delete_cart(user_id, cart_id, is_guest):
    """
    Deletes a cart from Firestore based on user_id or guestId.

    Parameters:
        user_id (str): The user ID of the logged-in user.
        cart_id (str): The cart ID for the cart to be deleted.
        is_guest (bool): Flag indicating whether the cart belongs to a guest or a logged-in user.
    """
    cart_ref = db.collection('carts')
    
    if is_guest:
        cart_query = cart_ref.where('guestId', '==', cart_id)
    else:
        cart_query = cart_ref.where('userId', '==', user_id)
    
    cart_snapshot = cart_query.stream()
    
    cart_doc_id = None  # To store the document ID

    # Look for the cart document
    for cart_doc in cart_snapshot:
        cart_doc_id = cart_doc.id
        break

    if cart_doc_id:
        try:
            # Delete the cart document
            cart_ref.document(cart_doc_id).delete()
            print(f"Cart with ID {cart_doc_id} deleted successfully.")
        except Exception as e:
            print(f"Error deleting cart: {str(e)}")
    else:
        print("No cart found to delete.")

@shopping.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    try:
        # Get data from request
        data = request.get_json()
        product_id = data.get('productId')
        quantity = data.get('quantity')
        size = data.get('size', "none")
        color = data.get('color', "none")
        isCartUpdate= data.get('isCartUpdate')
        old_size= data.get('old_size')
        old_color= data.get('old_color')

        logger.info(f"this is the oldcolor: {old_color}")
        logger.info(f"this is the newcolor: {color}")
        logger.info(f"this is the oldsixe: {old_size}")
        logger.info(f"this is the new size: {size}")



        # Get cart details from session
        user_data = get_cart_identifier()

        # Access the values from the returned dictionary
        user_id = user_data['userId']
        cart_id = user_data['cartId']
        is_guest = user_data['isGuest']
       
        logger.info(f"this is the isCartUpdate: {isCartUpdate}")
        
        # Validate input
        validate_input(product_id, quantity)

        # Fetch product details from Firestore
        product_ref = db.collection('products').document(product_id)
        product = product_ref.get()
        if not product.exists:
            return jsonify({'error': 'Product not found'}), 404

        product_data = product.to_dict()

        # Get or create cart
        cart_data = get_or_create_cart(user_id, cart_id, is_guest)
        total_items_count = 0  # Initialize total items count
        logger.info(f"updating cart {cart_data}")

        # Initialize existing_item_index to None before loop
        existing_item_index = None
        existing_item_index_for_old_cart = None

        for index, item in enumerate(cart_data['items']):
            if item['productId'] == product_id and item['size'] == size and item['color'] == color and not isCartUpdate:
                existing_item_index = index
                break
            if isCartUpdate and item['productId'] == product_id and item['size'] == old_size and item['color'] == old_color:
                existing_item_index_for_old_cart = index
                break
           

        
        # Ensure `existing_item_index` is checked before use
        
        if existing_item_index is not None:
            cart_data['items'][existing_item_index]['quantity'] += quantity
            logger.info(f"0001 : {cart_data}")
            logger.info(f"Updated existing item in cart: {product_id}")
        elif existing_item_index_for_old_cart is not None:
            cart_data['items'][existing_item_index_for_old_cart]['quantity'] = quantity
            cart_data['items'][existing_item_index_for_old_cart]['size'] = size
            cart_data['items'][existing_item_index_for_old_cart]['color'] = color
            logger.info(f"0002 : {cart_data}")
        else:
            cart_data['items'].append({
                'productId': product_id,
                'quantity': quantity,
                'size': size,
                'color': color,
            })
            logger.info(f"0003 : {cart_data}")

            logger.info(f"Added new item to cart: {product_id}")

        # Update the cart in Firestore
        cart_ref = db.collection('carts')
        cart_ref.document(cart_data['id']).update({'items': cart_data['items']})

        # Calculate total items count
        total_items_count = sum(item['quantity'] for item in cart_data['items'])
            


        # Store count in session
        session['cartCount'] = total_items_count

        # Return response
        action = 'updated' if existing_item_index is not None else 'inserted'
        return jsonify({
            'message': 'Product ' + ('updated' if action == 'updated' else 'added') + ' to cart',
            'action': action,
            'cartCount': total_items_count
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Add to cart error: {e}")
        return jsonify({'error': 'Server error', 'details': str(e)}), 500

@shopping.route('/get-cart-list', methods=['GET'])     
def get_cart_contents():
    logging.info('Starting getCartModalsContents function')

    try:
        # Get cart details from session
        user_data = get_cart_identifier()
        user_id = user_data['userId']
        cart_id = user_data['cartId']
        is_guest = user_data['isGuest']
        total = 0
        cart_Contents = []

        logging.info('Cart Identifier Details: %s', {'userId': user_id, 'cartId': cart_id, 'isGuest': is_guest})
        if is_guest:
            cart_ref = db.collection('carts').where('guestId', '==', cart_id)
        else:

            cart_ref = db.collection('carts').where('userId', '==', user_id)

        # Reference to the 'carts' collection
       
        cart_snapshot = cart_ref.stream()
        # Log the cart items by converting the snapshot into a list and printing the results
        cart_items = [doc.to_dict() for doc in cart_snapshot]
        logging.info(f"Cart items: {cart_items}")
        for cart in cart_items:
            items = cart.get('items', [])

            for item in items:
                product_id = item.get('productId')
                item['id'] = item.get('productId')
                qty = item.get('quantity') 
                logging.info(f"productId: {product_id}")
                product_ref = db.collection('products').document(product_id)
                product_snap = product_ref.get()
                if product_snap.exists:
                    product = product_snap.to_dict()
                    price= product.get('price')
                    imageUrl= product.get('imageUrl')
                    item['price'] = price
                    item['imageUrl'] = imageUrl
                    item['category']= product.get('category')
                    item['name']= product.get('name')
                    logging.info(f"product price is in  prod: {price}")
                
                else:
                    price= 0
                    logging.info(f"product in is not prod: ")
                
                cart_Contents.append(item)
                total += round(float(price) * qty, 2)
        logging.info(f"the content of itme : {cart_Contents}")
  
        logging.info(f"Total calculated: {total}")

        return render_template('cart-list.html', cartItems=cart_Contents,total=total )
        
    except Exception as e:
        print(f"Error fetching cart list: {str(e)}")
        return jsonify({'error': 'Error fetching cart list'}), 500
   

@shopping.route('/checkout', methods=['GET'])   
def checkout():
    logging.info('Starting getCartModalsContents function')

    try:
        # Fetch all products (optional, you can remove this part if not needed)
        products_ref = db.collection('products')
        products_snapshot = products_ref.stream()
        products = [{"id": doc.id, **doc.to_dict()} for doc in products_snapshot]

        # Get cart details from session
        user_data = get_cart_identifier()
        user_id = user_data['userId']
        cart_id = user_data['cartId']
        is_guest = user_data['isGuest']
        total = 0
        cart_Contents = []

        logging.info('Cart Identifier Details: %s', {'userId': user_id, 'cartId': cart_id, 'isGuest': is_guest})
        if is_guest:
            cart_ref = db.collection('carts').where('guestId', '==', cart_id)
        else:

            cart_ref = db.collection('carts').where('userId', '==', user_id)

        # Reference to the 'carts' collection
       
        cart_snapshot = cart_ref.stream()
        # Log the cart items by converting the snapshot into a list and printing the results
        cart_items = [doc.to_dict() for doc in cart_snapshot]
        logging.info(f"Cart items: {cart_items}")
        for cart in cart_items:
            items = cart.get('items', [])

            for item in items:
                product_id = item.get('productId')
                item['id'] = item.get('productId')
                qty = item.get('quantity') 
                logging.info(f"productId: {product_id}")
                product_ref = db.collection('products').document(product_id)
                product_snap = product_ref.get()
                if product_snap.exists:
                    product = product_snap.to_dict()
                    price= product.get('price')
                    imageUrl= product.get('imageUrl')
                    item['name']= product.get('name')
                    item['price'] = price
                    item['imageUrl'] = imageUrl
                    logging.info(f"product price is in  prod: {price}")
                
                else:
                    price= 0
                    logging.info(f"product in is not prod: ")
                
                cart_Contents.append(item)
                total += round(float(price) * qty, 2)
        logging.info(f"the content of itme : {cart_Contents}")
  
        logging.info(f"Total calculated: {total}")

        return render_template('checkout.html', cartItems=cart_Contents,total=total,products=products )
        
    except Exception as e:
        print(f"Error fetching cart list: {str(e)}")
        return jsonify({'error': 'Error fetching cart list'}), 500
   
@shopping.route('/delete-cart-item/<item_id>', methods=['POST'])
def delete_product(item_id):
    try:
        # Get cart details from session
        user_data = get_cart_identifier()
        user_id = user_data['userId']
        cart_id = user_data['cartId']
        is_guest = user_data['isGuest']

        # Determine the cart reference
        if is_guest:
            cart_ref = db.collection('carts').where('guestId', '==', cart_id)
        else:
            cart_ref = db.collection('carts').where('userId', '==', user_id)

        # Fetch the cart documents
        cart_snapshot = cart_ref.stream()
        cart_found = False

        for doc in cart_snapshot:
            cart = doc.to_dict()
            items = cart.get('items', [])
            
            # Check if the item exists and remove it
            updated_items = [item for item in items if item.get('productId') != item_id]

            if len(updated_items) != len(items):  # An item was removed
                cart_found = True
                # Update the document in Firestore
                doc.reference.update({'items': updated_items})
                flash(f"Product with ID '{item_id}' has been successfully deleted.", "success")
                break  # No need to check further carts

        if not cart_found:
            flash(f"Product with ID '{item_id}' not found in the cart.", "error")

    except Exception as e:
        logging.error(f"Error deleting product with ID {item_id}: {e}")
        flash("An error occurred while deleting the product. Please try again later.", "error")

    return redirect('/checkout')
 # Replace with the appropriate redirect route for your categories list

@shopping.route('/update-cart-item', methods=['POST'])
def update_cart_item():
    try:
        logging.info("Updating cart item...")

        # Get cart details from session
        user_data = get_cart_identifier()
        user_id = user_data['userId']
        cart_id = user_data['cartId']
        is_guest = user_data['isGuest']

        # Retrieve form values
        quantity = request.form.get('quantity', type=int)  # Matches 'name' in the form
        size = request.form.get('size', "none")
        color = request.form.get('color', "none")
        product_id = request.form.get('item_id')


        logging.info(f"Received item details - Quantity: {quantity}, Size: {size}, Color: {color}")

        doc_ref = db.collection('products').document(product_id)
        doc_snapshot = doc_ref.get()

        # Fetch all products (optional, you can remove this part if not needed)
        products_ref = db.collection('products')
        products_snapshot = products_ref.stream()
        products = [{"id": doc.id, **doc.to_dict()} for doc in products_snapshot]

        if doc_snapshot.exists:
            product = doc_snapshot.to_dict()
            product['old_qty']= quantity
            product['old_size']= size
            product['old_color']= color
            product['tag']= 'Update Cart'
            product['id']= product_id
            product['isCartUpdate']= True
            # Process images if available
            if 'imageUrl' in product:
                product['imageUrls'] = [
                    image_url.strip() for image_url in product['imageUrl'].split(',')
                ]

            # Process sizes if available
            if 'size' in product:
                product['sizes'] = [
                    size.strip() for size in product['size'].split(',')
                ]

            # Process colors if available
            if 'color' in product:
                product['colors'] = [
                    color.strip() for color in product['color'].split(',')
                ]

           # Get the user's cart    
            # Render the product details page with the product data and all products list
            logging.info(f"New product is : {product}")
            return render_template('product-details.html', product=product, products=products)
        # Save updated cart to Firestore
        #cart_ref = db.collection('carts').document(cart_id)
        #cart_ref.set({'items': cart_data['items']}, merge=True

    except Exception as e:
        logging.error(f"Error updating cart item: {str(e)}")
        return jsonify({'error': 'Error updating cart item'}), 500

@shopping.route('/send_order', methods=['POST'])
def send_order():
    logging.info('Starting send_order function')

    try:
        if request.method == 'POST':
            # Get customer details from the form
            full_name = request.form.get('full_name')
            email = request.form.get('email')
            tel = request.form.get('tel')

            # Email configuration
            sender_email = "manassekabongo29@gmail.com"
            sender_password = "yalb pbgj dgzy dcwb"
            subject = "New Order from ABCity"

            # Fetch all products (optional, you can remove this part if not needed)
            products_ref = db.collection('products')
            products_snapshot = products_ref.stream()
            products = [{"id": doc.id, **doc.to_dict()} for doc in products_snapshot]

            # Get cart details from session
            user_data = get_cart_identifier()
            user_id = user_data['userId']
            cart_id = user_data['cartId']
            is_guest = user_data['isGuest']
            total = 0
            cart_Contents = []

            logging.info('Cart Identifier Details: %s', {'userId': user_id, 'cartId': cart_id, 'isGuest': is_guest})
            if is_guest:
                cart_ref = db.collection('carts').where('guestId', '==', cart_id)
            else:
                cart_ref = db.collection('carts').where('userId', '==', user_id)

            # Reference to the 'carts' collection
            cart_snapshot = cart_ref.stream()
            # Log the cart items by converting the snapshot into a list and printing the results
            cart_items = [doc.to_dict() for doc in cart_snapshot]
            logging.info(f"Cart items: {cart_items}")
            for cart in cart_items:
                items = cart.get('items', [])

                for item in items:
                    product_id = item.get('productId')
                    item['id'] = item.get('productId')
                    qty = item.get('quantity') 
                    logging.info(f"productId: {product_id}")
                    product_ref = db.collection('products').document(product_id)
                    product_snap = product_ref.get()
                    if product_snap.exists:
                        product = product_snap.to_dict()
                        price = product.get('price')
                        imageUrl = product.get('imageUrl')
                        item['name'] = product.get('name')
                        item['price'] = price
                        item['imageUrl'] = imageUrl
                        logging.info(f"product price is in prod: {price}")
                    else:
                        price = 0
                        logging.info(f"product is not found: {product_id}")
                    
                    cart_Contents.append(item)
                    total += round(float(price) * qty, 2)

            # Prepare cart details to send in email (HTML formatted message)
            cart_details = ""
            for item in cart_Contents:
                cart_details += f"""
                    <tr>
                        <td>{item['name']}</td>
                        <td>{item['quantity']}</td>
                        <td>${item['price']}</td>
                        <td><img src="{item['imageUrl']}" alt="{item['name']}" width="50"></td>
                    </tr>
                """
            message = f"""
                <html>
                    <body>
                        <h2>New Order from ABCity</h2>
                        <p><strong>Full Name:</strong> {full_name}</p>
                        <p><strong>Email:</strong> {email}</p>
                        <p><strong>Phone:</strong> {tel}</p>
                        <h3>Cart Items:</h3>
                        <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 100%; margin-top: 15px;">
                            <thead>
                                <tr>
                                    <th>Product Name</th>
                                    <th>Quantity</th>
                                    <th>Price</th>
                                    <th>Image</th>
                                </tr>
                            </thead>
                            <tbody>
                                {cart_details}
                            </tbody>
                        </table>
                        <h3>Total: R{total}</h3>
                    </body>
                </html>
            """

            # Send email to admin or shop owner
            email_sent_admin = send_email(sender_email, sender_password, email, subject, message, is_html=True)

            # Send confirmation email to customer
            confirmation_message = f"""
                <html>
                    <body>
                        <h2>Order Confirmation</h2>
                        <p>Thank you for your order, {full_name}!</p>
                        <p>Your order has been successfully placed.</p>
                        <p><strong>Total:</strong> R{total}</p>
                        <p>We will contact you soon for further details.</p>
                    </body>
                </html>
            """
            email_sent_customer = send_email(sender_email, sender_password, email, "Order Confirmation", confirmation_message, is_html=True)

            # If both emails are successfully sent, delete the cart
            if email_sent_admin and email_sent_customer:
                # Delete the cart after successful email sending
                delete_cart(user_id, cart_id, is_guest)
                logging.info(f"Cart with ID {cart_id} deleted after order is placed.")

            logging.info(f"the content of cart items : {cart_Contents}")
            logging.info(f"Total calculated: {total}")

            return redirect('/')  # Redirect to a success page

    except Exception as e:
        logging.error(f"Error sending order: {str(e)}")
        return jsonify({'error': 'Error sending order'}), 500



@shopping.route('/order_success')
def order_success():
    return "Your order has been placed successfully!"


# Path to store WhatsApp session credentials
SESSION_FILE = 'whatsapp_session.json'

class WhatsAppAutomation:
    def __init__(self, browser_type='chrome'):
        self.driver = None
        self.browser_type = browser_type.lower()
        self.setup_driver()

    def setup_driver(self):
        """Setup the browser driver based on the specified browser type."""
        try:
            if self.browser_type == 'chrome':
                options = Options()
                options.add_argument('--headless')  # Run in headless mode
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--window-size=1920,1080')

                # ✅ Correct method name
                options.add_experimental_option('excludeSwitches', ['enable-automation'])
                options.add_experimental_option('useAutomationExtension', False)

                self.driver = webdriver.Chrome(options=options)
            
            logging.info(f"{self.browser_type.capitalize()} driver initialized successfully")
            
        except Exception as e:
            logging.error(f"Failed to initialize {self.browser_type} driver: {str(e)}")
            raise


    def extract_qr_code(self):
        """Extract the QR code image from WhatsApp Web and provide it as base64 for scanning."""
        try:
            logging.info("Waiting for QR code to be visible...")
            
            # Wait for the QR code canvas element to be present
            qr_element = WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH, "//canvas[@aria-label='Scan me!']"))
            )

            # Capture the QR code as a base64 image
            qr_code_base64 = self.driver.execute_script("""
                var canvas = document.querySelector('canvas[aria-label="Scan me!"]');
                return canvas.toDataURL('image/png');
            """)

            logging.info("QR code extracted successfully.")
            return qr_code_base64  # Return the base64 string of the QR code
        
        except Exception as e:
            logging.error(f"Failed to extract QR code: {str(e)}")
            return None

    def login_to_whatsapp(self):
        """Login to WhatsApp Web."""
        try:
            self.driver.delete_all_cookies()
            self.driver.get("https://web.whatsapp.com")
            
            # Extract the QR code
            qr_code_base64 = self.extract_qr_code()
            if not qr_code_base64:
                raise Exception("Failed to extract QR code")
            
            logging.info("QR code ready for scanning.")
            
            # Wait for successful login (QR code disappears)
            WebDriverWait(self.driver, 60).until_not(
                EC.presence_of_element_located((By.XPATH, "//canvas[@aria-label='Scan me!']"))
            )
            
            logging.info("Successfully logged into WhatsApp Web")
            self.save_session()
            return qr_code_base64  # Return QR code base64 to the user for scanning
            
        except Exception as e:
            logging.error(f"Error during login process: {str(e)}")
            return None

    def save_session(self):
        """Save the current session credentials to a file."""
        try:
            cookies = self.driver.get_cookies()
            local_storage = self.driver.execute_script("return window.localStorage;")
            
            with open(SESSION_FILE, 'w') as f:
                json.dump({
                    'cookies': cookies,
                    'local_storage': local_storage
                }, f)
            
            logging.info("Session credentials saved successfully.")
        except Exception as e:
            logging.error(f"Failed to save session credentials: {str(e)}")

    def load_session(self):
        """Load session credentials from a file."""
        try:
            if not os.path.exists(SESSION_FILE):
                logging.info("No session file found.")
                return False
            
            with open(SESSION_FILE, 'r') as f:
                session_data = json.load(f)
            
            self.driver.get("https://web.whatsapp.com")
            self.driver.delete_all_cookies()
            for cookie in session_data['cookies']:
                self.driver.add_cookie(cookie)
            
            for key, value in session_data['local_storage'].items():
                self.driver.execute_script(f"window.localStorage.setItem('{key}', '{value}');")
            
            self.driver.refresh()
            
            logging.info("Session credentials loaded successfully.")
            return True
        except Exception as e:
            logging.error(f"Failed to load session credentials: {str(e)}")
            return False

    def login_check(self) -> bool:
        """Check if the user is already logged in."""
        try:
            self.driver.get("https://web.whatsapp.com")
            time.sleep(5)  # Allow initial load

            # Check for chat list
            if WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@id='side']"))
            ):
                qr_code_present = False
                try:
                    WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, "//canvas[@aria-label='Scan me!']"))
                    )
                    qr_code_present = True
                except TimeoutException:
                    pass  # QR code not found

                if not qr_code_present:
                    logging.info("WhatsApp Web is already logged in.")
                    return True
            
            return False
        except TimeoutException:
            logging.info("WhatsApp Web is not logged in.")
            return False

    def cleanup(self):
        """Cleanup browser session."""
        if self.driver:
            try:
                self.driver.quit()
                logging.info("Browser session cleaned up")
            except Exception as e:
                logging.error(f"Error during cleanup: {str(e)}")

# Route for WhatsApp login and session management


# def setup_whatsapp():
#     try:
#         whatsapp = WhatsAppAutomation()

#         # Check if already logged in
#         if whatsapp.login_check():
#             whatsapp.cleanup()
#             return jsonify({'message': 'WhatsApp Web already logged in'}), 200

#         # Attempt to load session
#         if whatsapp.load_session():
#             whatsapp.cleanup()
#             return jsonify({'message': 'Session loaded successfully'}), 200

#         # Log in if session isn't available
#         if not whatsapp.login_to_whatsapp():
#             raise Exception("Failed to log into WhatsApp Web")

#         # Save session credentials after successful login
#         whatsapp.save_session()

#         return jsonify({'message': 'QR code scanned, WhatsApp Web logged in successfully'}), 200

#     except Exception as e:
#         logging.error(f"Error in WhatsApp setup: {str(e)}", exc_info=True)
#         return jsonify({'error': f'Failed to initialize WhatsApp setup: {str(e)}'}), 500
