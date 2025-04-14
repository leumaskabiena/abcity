# import logging
# import time
# import datetime
# import pywhatkit as kit
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.service import Service  # Correct import for Service


# from flask import Blueprint, render_template, current_app, jsonify, request, session, redirect, flash
# from google.cloud import firestore

# # Configure logging
# logging.basicConfig(level=logging.INFO)  # Change to DEBUG for more detailed logs
# logger = logging.getLogger(__name__)

# # Create the blueprint and give it a unique name
# shopping = Blueprint('shopping', __name__)

# # Initialize Firestore client
# db = firestore.Client()

# def is_logged_into_whatsapp(driver):
#     try:
#         # Check if QR code exists
#         qr_code = driver.find_elements(By.XPATH, "//canvas")
#         if qr_code:
#             logging.info("QR code detected. Please log in to WhatsApp Web.")
#             return False  # Not logged in
#         else:
#             logging.info("Already logged into WhatsApp Web.")
#             return True  # Logged in
#     except Exception as e:
#         logging.error(f"Error checking WhatsApp login status: {e}")
#         return False

# def get_cart_identifier():
#     if 'userId' in session:
#         logger.info(f"User identified with userId: {session['userId']}")
#         return {'userId': session['userId'], 'cartId': None, 'isGuest': False}
#     else:
#         if 'cartId' not in session:
#             session['cartId'] = str(int(time.time()))  # Generate a cart ID for guest users
#             logger.info(f"Generated new cartId for guest: {session['cartId']}")
#         else:
#             logger.info(f"Using existing cartId for guest: {session['cartId']}")
#         return {'userId': None, 'cartId': session['cartId'], 'isGuest': True}

# def validate_input(product_id, quantity):
#     if not product_id or not quantity:
#         raise ValueError('Invalid input, missing: ' + ('productId' if not product_id else 'quantity'))

# def get_or_create_cart(user_id, cart_id, is_guest):
#     cart_ref = db.collection('carts')
    
#     if is_guest:
#         cart_query = cart_ref.where('guestId', '==', cart_id)
#     else:
#         cart_query = cart_ref.where('userId', '==', user_id)
    
#     cart_snapshot = cart_query.stream()

#     cart_data = None
#     cart_doc_id = None  # To store the document ID

#     for cart_doc in cart_snapshot:
#         cart_data = cart_doc.to_dict()
#         cart_doc_id = cart_doc.id  # Capture the document ID
#         break

#     if not cart_data:
#         # Create a new cart if no cart exists
#         new_cart_ref = cart_ref.add({
#             'guestId' if is_guest else 'userId': cart_id if is_guest else user_id,
#             'items': []
#         })
#         # Return the newly created cart data, including document ID
#         cart_data = {
#             'id': new_cart_ref.id,  # Document ID
#             'items': []
#         }
#         return cart_data  # Return new cart data

#     # Return existing cart data, including document ID
#     cart_data['id'] = cart_doc_id
#     return cart_data


# @shopping.route('/add-to-cart', methods=['POST'])
# def add_to_cart():
#     try:
#         # Get data from request
#         data = request.get_json()
#         product_id = data.get('productId')
#         quantity = data.get('quantity')
#         size = data.get('size', "none")
#         color = data.get('color', "none")
#         isCartUpdate= data.get('isCartUpdate')
#         old_size= data.get('old_size')
#         old_color= data.get('old_color')

#         logger.info(f"this is the oldcolor: {old_color}")
#         logger.info(f"this is the newcolor: {color}")
#         logger.info(f"this is the oldsixe: {old_size}")
#         logger.info(f"this is the new size: {size}")



#         # Get cart details from session
#         user_data = get_cart_identifier()

#         # Access the values from the returned dictionary
#         user_id = user_data['userId']
#         cart_id = user_data['cartId']
#         is_guest = user_data['isGuest']
       
#         logger.info(f"this is the isCartUpdate: {isCartUpdate}")
        
#         # Validate input
#         validate_input(product_id, quantity)

#         # Fetch product details from Firestore
#         product_ref = db.collection('products').document(product_id)
#         product = product_ref.get()
#         if not product.exists:
#             return jsonify({'error': 'Product not found'}), 404

#         product_data = product.to_dict()

#         # Get or create cart
#         cart_data = get_or_create_cart(user_id, cart_id, is_guest)
#         total_items_count = 0  # Initialize total items count
#         logger.info(f"updating cart {cart_data}")

#         # Initialize existing_item_index to None before loop
#         existing_item_index = None
#         existing_item_index_for_old_cart = None

#         for index, item in enumerate(cart_data['items']):
#             if item['productId'] == product_id and item['size'] == size and item['color'] == color and not isCartUpdate:
#                 existing_item_index = index
#                 break
#             if isCartUpdate and item['productId'] == product_id and item['size'] == old_size and item['color'] == old_color:
#                 existing_item_index_for_old_cart = index
#                 break
           

        
#         # Ensure `existing_item_index` is checked before use
        
#         if existing_item_index is not None:
#             cart_data['items'][existing_item_index]['quantity'] += quantity
#             logger.info(f"0001 : {cart_data}")
#             logger.info(f"Updated existing item in cart: {product_id}")
#         elif existing_item_index_for_old_cart is not None:
#             cart_data['items'][existing_item_index_for_old_cart]['quantity'] = quantity
#             cart_data['items'][existing_item_index_for_old_cart]['size'] = size
#             cart_data['items'][existing_item_index_for_old_cart]['color'] = color
#             logger.info(f"0002 : {cart_data}")
#         else:
#             cart_data['items'].append({
#                 'productId': product_id,
#                 'quantity': quantity,
#                 'size': size,
#                 'color': color,
#             })
#             logger.info(f"0003 : {cart_data}")

#             logger.info(f"Added new item to cart: {product_id}")

#         # Update the cart in Firestore
#         cart_ref = db.collection('carts')
#         cart_ref.document(cart_data['id']).update({'items': cart_data['items']})

#         # Calculate total items count
#         total_items_count = sum(item['quantity'] for item in cart_data['items'])
            


#         # Store count in session
#         session['cartCount'] = total_items_count

#         # Return response
#         action = 'updated' if existing_item_index is not None else 'inserted'
#         return jsonify({
#             'message': 'Product ' + ('updated' if action == 'updated' else 'added') + ' to cart',
#             'action': action,
#             'cartCount': total_items_count
#         })

#     except ValueError as e:
#         return jsonify({'error': str(e)}), 400
#     except Exception as e:
#         logger.error(f"Add to cart error: {e}")
#         return jsonify({'error': 'Server error', 'details': str(e)}), 500

# @shopping.route('/get-cart-list', methods=['GET'])     
# def get_cart_contents():
#     logging.info('Starting getCartModalsContents function')

#     try:
#         # Get cart details from session
#         user_data = get_cart_identifier()
#         user_id = user_data['userId']
#         cart_id = user_data['cartId']
#         is_guest = user_data['isGuest']
#         total = 0
#         cart_Contents = []

#         logging.info('Cart Identifier Details: %s', {'userId': user_id, 'cartId': cart_id, 'isGuest': is_guest})
#         if is_guest:
#             cart_ref = db.collection('carts').where('guestId', '==', cart_id)
#         else:

#             cart_ref = db.collection('carts').where('userId', '==', user_id)

#         # Reference to the 'carts' collection
       
#         cart_snapshot = cart_ref.stream()
#         # Log the cart items by converting the snapshot into a list and printing the results
#         cart_items = [doc.to_dict() for doc in cart_snapshot]
#         logging.info(f"Cart items: {cart_items}")
#         for cart in cart_items:
#             items = cart.get('items', [])

#             for item in items:
#                 product_id = item.get('productId')
#                 item['id'] = item.get('productId')
#                 qty = item.get('quantity') 
#                 logging.info(f"productId: {product_id}")
#                 product_ref = db.collection('products').document(product_id)
#                 product_snap = product_ref.get()
#                 if product_snap.exists:
#                     product = product_snap.to_dict()
#                     price= product.get('price')
#                     imageUrl= product.get('imageUrl')
#                     item['price'] = price
#                     item['imageUrl'] = imageUrl
#                     item['category']= product.get('category')
#                     item['name']= product.get('name')
#                     logging.info(f"product price is in  prod: {price}")
                
#                 else:
#                     price= 0
#                     logging.info(f"product in is not prod: ")
                
#                 cart_Contents.append(item)
#                 total += round(float(price) * qty, 2)
#         logging.info(f"the content of itme : {cart_Contents}")
  
#         logging.info(f"Total calculated: {total}")

#         return render_template('cart-list.html', cartItems=cart_Contents,total=total )
        
#     except Exception as e:
#         print(f"Error fetching cart list: {str(e)}")
#         return jsonify({'error': 'Error fetching cart list'}), 500
   

# @shopping.route('/checkout', methods=['GET'])   
# def checkout():
#     logging.info('Starting getCartModalsContents function')

#     try:
#         # Fetch all products (optional, you can remove this part if not needed)
#         products_ref = db.collection('products')
#         products_snapshot = products_ref.stream()
#         products = [{"id": doc.id, **doc.to_dict()} for doc in products_snapshot]

#         # Get cart details from session
#         user_data = get_cart_identifier()
#         user_id = user_data['userId']
#         cart_id = user_data['cartId']
#         is_guest = user_data['isGuest']
#         total = 0
#         cart_Contents = []

#         logging.info('Cart Identifier Details: %s', {'userId': user_id, 'cartId': cart_id, 'isGuest': is_guest})
#         if is_guest:
#             cart_ref = db.collection('carts').where('guestId', '==', cart_id)
#         else:

#             cart_ref = db.collection('carts').where('userId', '==', user_id)

#         # Reference to the 'carts' collection
       
#         cart_snapshot = cart_ref.stream()
#         # Log the cart items by converting the snapshot into a list and printing the results
#         cart_items = [doc.to_dict() for doc in cart_snapshot]
#         logging.info(f"Cart items: {cart_items}")
#         for cart in cart_items:
#             items = cart.get('items', [])

#             for item in items:
#                 product_id = item.get('productId')
#                 item['id'] = item.get('productId')
#                 qty = item.get('quantity') 
#                 logging.info(f"productId: {product_id}")
#                 product_ref = db.collection('products').document(product_id)
#                 product_snap = product_ref.get()
#                 if product_snap.exists:
#                     product = product_snap.to_dict()
#                     price= product.get('price')
#                     imageUrl= product.get('imageUrl')
#                     item['name']= product.get('name')
#                     item['price'] = price
#                     item['imageUrl'] = imageUrl
#                     logging.info(f"product price is in  prod: {price}")
                
#                 else:
#                     price= 0
#                     logging.info(f"product in is not prod: ")
                
#                 cart_Contents.append(item)
#                 total += round(float(price) * qty, 2)
#         logging.info(f"the content of itme : {cart_Contents}")
  
#         logging.info(f"Total calculated: {total}")

#         return render_template('checkout.html', cartItems=cart_Contents,total=total,products=products )
        
#     except Exception as e:
#         print(f"Error fetching cart list: {str(e)}")
#         return jsonify({'error': 'Error fetching cart list'}), 500
   
# @shopping.route('/delete-cart-item/<item_id>', methods=['POST'])
# def delete_product(item_id):
#     try:
#         # Get cart details from session
#         user_data = get_cart_identifier()
#         user_id = user_data['userId']
#         cart_id = user_data['cartId']
#         is_guest = user_data['isGuest']

#         # Determine the cart reference
#         if is_guest:
#             cart_ref = db.collection('carts').where('guestId', '==', cart_id)
#         else:
#             cart_ref = db.collection('carts').where('userId', '==', user_id)

#         # Fetch the cart documents
#         cart_snapshot = cart_ref.stream()
#         cart_found = False

#         for doc in cart_snapshot:
#             cart = doc.to_dict()
#             items = cart.get('items', [])
            
#             # Check if the item exists and remove it
#             updated_items = [item for item in items if item.get('productId') != item_id]

#             if len(updated_items) != len(items):  # An item was removed
#                 cart_found = True
#                 # Update the document in Firestore
#                 doc.reference.update({'items': updated_items})
#                 flash(f"Product with ID '{item_id}' has been successfully deleted.", "success")
#                 break  # No need to check further carts

#         if not cart_found:
#             flash(f"Product with ID '{item_id}' not found in the cart.", "error")

#     except Exception as e:
#         logging.error(f"Error deleting product with ID {item_id}: {e}")
#         flash("An error occurred while deleting the product. Please try again later.", "error")

#     return redirect('/checkout')
#  # Replace with the appropriate redirect route for your categories list

# @shopping.route('/update-cart-item', methods=['POST'])
# def update_cart_item():
#     try:
#         logging.info("Updating cart item...")

#         # Get cart details from session
#         user_data = get_cart_identifier()
#         user_id = user_data['userId']
#         cart_id = user_data['cartId']
#         is_guest = user_data['isGuest']

#         # Retrieve form values
#         quantity = request.form.get('quantity', type=int)  # Matches 'name' in the form
#         size = request.form.get('size', "none")
#         color = request.form.get('color', "none")
#         product_id = request.form.get('item_id')


#         logging.info(f"Received item details - Quantity: {quantity}, Size: {size}, Color: {color}")

#         doc_ref = db.collection('products').document(product_id)
#         doc_snapshot = doc_ref.get()

#         # Fetch all products (optional, you can remove this part if not needed)
#         products_ref = db.collection('products')
#         products_snapshot = products_ref.stream()
#         products = [{"id": doc.id, **doc.to_dict()} for doc in products_snapshot]

#         if doc_snapshot.exists:
#             product = doc_snapshot.to_dict()
#             product['old_qty']= quantity
#             product['old_size']= size
#             product['old_color']= color
#             product['tag']= 'Update Cart'
#             product['id']= product_id
#             product['isCartUpdate']= True
#             # Process images if available
#             if 'imageUrl' in product:
#                 product['imageUrls'] = [
#                     image_url.strip() for image_url in product['imageUrl'].split(',')
#                 ]

#             # Process sizes if available
#             if 'size' in product:
#                 product['sizes'] = [
#                     size.strip() for size in product['size'].split(',')
#                 ]

#             # Process colors if available
#             if 'color' in product:
#                 product['colors'] = [
#                     color.strip() for color in product['color'].split(',')
#                 ]

#            # Get the user's cart    
#             # Render the product details page with the product data and all products list
#             logging.info(f"New product is : {product}")
#             return render_template('product-details.html', product=product, products=products)
#         # Save updated cart to Firestore
#         #cart_ref = db.collection('carts').document(cart_id)
#         #cart_ref.set({'items': cart_data['items']}, merge=True

#     except Exception as e:
#         logging.error(f"Error updating cart item: {str(e)}")
#         return jsonify({'error': 'Error updating cart item'}), 500


# @shopping.route('/send_order', methods=['POST'])
# def send_order():
#     try:
#         # Get form data with validation
#         name = request.form.get('full_name')
#         email = request.form.get('email')
#         tel = request.form.get('tel')

#         # Basic validation
#         if not all([name, email, tel]):
#             return jsonify({
#                 'error': 'Missing required fields'
#             }), 400

#         # Email validation
#         if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
#             return jsonify({
#                 'error': 'Invalid email format'
#             }), 400

#         # Log received data
#         logging.info(f"Received order data: Name={name}, Email={email}, Tel={tel}")

#         # Instead of pywhatkit, consider using WhatsApp Business API
#         # or other production-ready alternatives
#         try:
#             # Example using WhatsApp Business API (you'll need to implement this)
#             response = send_whatsapp_message(
#                 to_number="+27619722887",
#                 message=f"Hello {name}, this is a test message from Python! Your email is {email} and phone number is {tel}."
#             )
            
#             return jsonify({
#                 'message': 'Order processed and WhatsApp message sent successfully!',
#                 'message_id': response.get('message_id')
#             }), 200

#         except WhatsAppAPIError as wa_error:
#             logging.error(f"WhatsApp API error: {wa_error}")
#             return jsonify({
#                 'error': 'Failed to send WhatsApp message',
#                 'details': str(wa_error)
#             }), 503

#     except Exception as e:
#         logging.error(f"Error processing order: {e}")
#         return jsonify({
#             'error': 'Internal server error',
#             'details': str(e)
#         }), 500

# def send_whatsapp_message(to_number: str, message: str) -> dict:
#     """
#     Implement this function using WhatsApp Business API
#     or another production-ready messaging service
#     """
#     raise NotImplementedError("Replace with actual WhatsApp Business API implementation")