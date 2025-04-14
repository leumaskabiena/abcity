import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session, Blueprint
from firebase_admin import credentials, firestore, initialize_app
from werkzeug.security import check_password_hash,  generate_password_hash

# Create the blueprint and give it a unique name
auth = Blueprint('auth', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)  # Change to DEBUG for more detailed logs
logger = logging.getLogger(__name__)

# Initialize Firestore client
db = firestore.Client()

@auth.route("/login", methods=["GET", "POST"])
def login():
    # Fetch all products (optional, you can remove this part if not needed)
    products_ref = db.collection('products')
    products_snapshot = products_ref.stream()
    products = [{"id": doc.id, **doc.to_dict()} for doc in products_snapshot]
    
    if request.method == 'POST':
        # Retrieve form data (email and password from the login form)
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            # Query Firestore for the user with the matching email
            users_ref = db.collection('users')
            user_query = users_ref.where('email', '==', email).stream()
            user = None
            user_id = None
            for doc in user_query:
                user = doc.to_dict()
                user_id = doc.id
                break

            # Handle case where the user is not found
            if not user:
                flash('Invalid email or password', 'error')
                return redirect('/login')
            
            # Verify the provided password against the stored hashed password
            if not check_password_hash(user['password'], password):
                flash('Invalid email or password', 'error')
                return redirect('/login')
            
            # Log user details for debugging (avoid logging sensitive data)
            logging.info('User logged in: %s', {'user_id': user_id, 'user_name': user.get('name')})

            # Store user info in the session
            session['userId'] = user_id
            session['user_name'] = user.get('name')
            session['isAuthenticated'] = True

            # Redirect to the homepage after successful login
            return redirect('/')

        except Exception as e:
            # Log errors for debugging
            logging.error(f"Error during login: {e}")
            flash('An internal error occurred. Please try again later.', 'error')
            return redirect('/login')

    # Render the login template with the form and optional product data
    return render_template('login.html', products=products)



@auth.route('/logout')
def logout():
    session.clear()
    # Redirect to the login page or home page
    return redirect('/')

@auth.route('/sign-up', methods=["GET", "POST"])
def sign_up():
    # Fetch all products (optional, you can remove this part if not needed)
    products_ref = db.collection('products')
    products_snapshot = products_ref.stream()
    products = [{"id": doc.id, **doc.to_dict()} for doc in products_snapshot]

    # Only process POST requests
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')  
        confirm_pass = request.form.get('confirm_pass')  
        logging.info('User Details: %s', {'email': email, 'password': password, 'confirm_pass': confirm_pass})

        # Check if passwords match
        if password != confirm_pass:
            flash('Passwords do not match!', 'error')
            return redirect('/sign-up')

        # Check if email already exists in the database
        users_ref = db.collection('users')
        user_query = users_ref.where('email', '==', email).stream()
        user = None
        for doc in user_query:
            user = doc.to_dict()
            user['id'] = doc.id  # Add document ID to user data
            break

        if user:
            flash('User already exists!', 'error')
            return redirect('/sign-up')

        try:
            # Hash the password before storing it
            hashed_password = generate_password_hash(password)

            # Add the new user to Firestore
            users_ref.add({
                'name': name,
                'email': email,
                'password': hashed_password
            })
            flash('User successfully registered!', 'success')
            return redirect('/login')  # Redirect to the login page after successful sign-up

        except Exception as e:
            logging.error(f"Error during sign-up: {e}")
            flash('An error occurred during sign-up. Please try again later.', 'error')
            return redirect('/sign-up')

    # Render the sign-up form if the method is GET
    return render_template('sign-up.html', products=products)
