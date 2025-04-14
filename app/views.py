import logging
from flask import Blueprint, render_template, current_app, jsonify, request, redirect, flash
from google.cloud import firestore
from datetime import datetime, timedelta

views = Blueprint('views',__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)  # Change to DEBUG for more detailed logs
logger = logging.getLogger(__name__)

# Initialize Firestore client
db = firestore.Client()


@views.route('/')
def home():
    try:
        # Log the start of the function
        logger.info("GET /get-all-products endpoint accessed.")

        # Fetch products from Firestore
        products_ref = db.collection("products")
        products_snapshot = products_ref.stream()
        all_products = [
            {"id": doc.id, **doc.to_dict()} for doc in products_snapshot
        ]
        logger.info(f"Retrieved {len(all_products)} products from Firestore.")

        # Fetch categories from Firestore
        categories_ref = db.collection("categories")
        categories_snapshot = categories_ref.stream()
        categories = [
            {"id": doc.id, **doc.to_dict()} for doc in categories_snapshot
        ]
        logger.info(f"Retrieved {len(categories)} categories from Firestore.")

        # Extract category parameter
        ctg = request.args.get("ctg")
        logger.info(f"Category parameter received: {ctg}")

        # Filter products by category if 'ctg' is provided
        products = all_products
        if ctg:
            category_exists = any(
                category["name"].lower() == ctg.lower() for category in categories
            )

            if category_exists:
                products = [
                    product for product in all_products
                    if product.get("category", "").lower() == ctg.lower()
                ]
                logger.info(
                    f"Filtered products by category '{ctg}', found {len(products)} products."
                )
            else:
                logger.warning(f"Category '{ctg}' not found.")
                return jsonify({"error": f"Category '{ctg}' not found."}), 404

        # Fetch the last items added by category
        categories_in_products = list({product["category"] for product in products})
        last_items = []
        for category in categories_in_products:
            last_item = next(
                (product for product in reversed(products)
                 if product.get("category") == category),
                None,
            )
            if last_item:
                last_items.append({
                    "category": category,
                    "description": last_item.get("description"),
                    "imageUrl": last_item.get("imageUrl"),
                })

        logger.info(f"Retrieved {len(last_items)} last items by category.")

        # Render the layout template
        return render_template(
            "home.html",
            products=products,
            categories=categories,
            lastItems=last_items
        )
    except Exception as e:
        logger.error(f"Error fetching products: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    

@views.route('/product-details')
def get_product_details():
    try:
        # Get the product ID from the query parameter
        product_id = request.args.get('id')

        if not product_id:
            return jsonify({'error': 'Product ID is missing'}), 400  # Handle missing product ID

        # Fetch the product by ID
        doc_ref = db.collection('products').document(product_id)
        doc_snapshot = doc_ref.get()

        # Fetch all products (optional, you can remove this part if not needed)
        products_ref = db.collection('products')
        products_snapshot = products_ref.stream()
        products = [{"id": doc.id, **doc.to_dict()} for doc in products_snapshot]

        # Fetch all categories (optional, you can remove this part if not needed)
        categories_ref = db.collection('categories')
        categories_snapshot = categories_ref.stream()
        categories = [{"id": doc.id, **doc.to_dict()} for doc in categories_snapshot]

        if doc_snapshot.exists:
            product = doc_snapshot.to_dict()

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

            # Add the document ID to the product object
            product['id'] = doc_snapshot.id
            print('Server-side product data received:', product)

            # Render the product details page with the product data and all products list
            return render_template('product-details.html', product=product, products=products)
        else:
            return jsonify({'error': 'Product not found'}), 404

    except Exception as e:
        print(f"Error fetching product: {str(e)}")
        return jsonify({'error': 'Error fetching product'}), 500

@views.route('/create-product',methods=["GET", "POST"])
def create_product():
    # Calculate the timestamp for 3 hour ago
    one_hour_ago = datetime.utcnow() - timedelta(hours=3)
    # Fetch all products (optional, you can remove this part if not needed)
    products_ref = db.collection('products')
    # Query for products created within the last 3 hour
    query = products_ref.where('createdAt', '>=', one_hour_ago)
    products_snapshot = query.stream()
    products = [{"id": doc.id, **doc.to_dict()} for doc in products_snapshot]

    # Fetch categories from Firestore
    categories_ref = db.collection("categories")
    categories_snapshot = categories_ref.stream()
    categories = [{"id": doc.id, **doc.to_dict()} for doc in categories_snapshot]

    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        category = request.form.get('category')
        color = request.form.get('color')
        size = request.form.get('size')
        description = request.form.get('description')
        imageUrl = request.form.get('imageUrl')
        try:
            products_ref.add({
                'name': name,
                'price': price,
                'category': category,
                'color': color,
                'size': size,
                'description': description,
                'imageUrl': imageUrl,
                'createdAt': datetime.utcnow()  # Add createdAt timestamp
            })
            flash('Product successfully created!', 'success')
        except Exception as e:
            logging.error(f"Error during creation of the product : {e}")
            flash('An error occurred during creation. Please try again later.', 'error')
            return redirect('/create-product')


    # Redirect to the login page or home page
    return render_template('product.html',products=products,categories=categories)

@views.route('/create-category',methods=["POST"])
def create_category():
    category_name = request.form.get('category_name')
    # Fetch categories from Firestore
    categories_ref = db.collection("categories")
    try:
        categories_ref.add({
            'name': category_name
        })
        flash('Category successfully created!', 'success')
    except Exception as e:
        logging.error(f"Error during creation of the product : {e}")
        flash('An error occurred during creation. Please try again later.', 'error')
        return redirect('/create-product')
    return  redirect('/create-product')

@views.route('/edit-product/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if request.method == 'POST':
        # Retrieve form data
        name = request.form.get('name')
        price = request.form.get('price')
        category = request.form.get('category')
        color = request.form.get('color')
        size = request.form.get('size')
        description = request.form.get('description')
        imageUrl = request.form.get('imageUrl')

        try:
            # Update the product in Firestore
            db.collection('products').document(product_id).update({
                'name': name,
                'price': price,
                'category': category,
                'color': color,
                'size': size,
                'description': description,
                'imageUrl': imageUrl,
                'updatedAt': datetime.utcnow()  # Updated timestamp instead of 'createdAt'
            })
            flash('Product updated successfully', 'success')
            return redirect(f'/product-details?id={product_id}')  # Redirect to product details
        except Exception as e:
            logging.error(f"Error during updating the product: {e}")
            flash('An error occurred during updating. Please try again later.', 'error')
            return redirect(f'/edit-product/{product_id}')  # Redirect back to edit form

    # Fetch product details and categories for the GET request
    product = db.collection('products').document(product_id).get().to_dict()
    if product:
        product['id'] = product_id
    categories = [cat.to_dict() for cat in db.collection('categories').stream()]
    logging.error(f"Error during updating the productssssss:{product}")
    return render_template('edit-product.html', product=product, categories=categories)


@views.route('/update-category-name', methods=['POST'])
def update_category_name():
    name_old_name = request.form.get('name_old_name')
    name_new_name = request.form.get('name_new_name')
    
    if not name_old_name or not name_new_name:
        flash("Both old name and new name are required.", "error")
        return redirect('/categories')  # Replace with your category list page

    try:
        # Query to find the category by the old name
        categories_ref = db.collection('categories')
        query = categories_ref.where('name', '==', name_old_name)
        docs = query.stream()
        
        # Update the category name for each matching document
        updated = False
        for doc in docs:
            doc.reference.update({'name': name_new_name})
            updated = True
        
        if updated:
            flash(f"Category '{name_old_name}' successfully updated to '{name_new_name}'.", "success")
        else:
            flash(f"No category found with the name '{name_old_name}'.", "error")
        
    except Exception as e:
        logging.error(f"Error updating category name: {e}")
        flash("An error occurred while updating the category. Please try again later.", "error")

    return redirect('/categories')  # Replace with your category list page

@views.route('/delete-product/<product_id>', methods=['POST'])
def delete_product(product_id):
    try:
        # Delete the category document from Firestore
        logging.info(f"product is about to be deleted with id of : {product_id}")
        db.collection('products').document(product_id).delete()
        flash(f"Product with ID '{product_id}' has been successfully deleted.", "success")
    except Exception as e:
        logging.error(f"Error deleting category with ID {product_id}: {e}")
        flash("An error occurred while deleting the category. Please try again later.", "error")
    return redirect('/')  # Replace with the appropriate redirect route for your categories list


@views.route('/about-us')
def about_us():
    return render_template('about-us.html')