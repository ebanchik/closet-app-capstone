import db
from db import connect_to_db
from flask import Flask, request, jsonify, make_response, render_template, send_from_directory
from flask_login import LoginManager, UserMixin, current_user
from db import check_password
from decouple import config
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import logging
import jwt
from datetime import datetime, timedelta
from auth import get_user_id_from_jwt
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

import importlib.metadata

flask_login_version = importlib.metadata.version("Flask-Login")
print(flask_login_version)

app = Flask(__name__)
app.debug = True

secret_key = config("SECRET_KEY", default="default_secret_key")
app.secret_key = secret_key

load_dotenv()

CORS(app, supports_credentials=True, origins='http://localhost:5173', allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "PATCH", "DELETE"])

app.config.update({
    'SESSION_COOKIE_DOMAIN': None,  # Set to your domain if needed
    'SESSION_COOKIE_PATH': '/',
    'SESSION_COOKIE_HTTPONLY': True,
    'SESSION_COOKIE_SECURE': False,  # Set to True if using HTTPS
    'SESSION_COOKIE_SAMESITE': 'Lax',
})

# Initialize the LoginManager
login_manager = LoginManager(app)
login_manager.login_view = "login"

@app.route('/')
def home():
    if current_user.is_authenticated:
        return f'Hello, {current_user.email}! You are logged in.'
    else:
        return 'Hello, Guest!'

############################# ITEMS ROUTES #########################

@app.route("/items.json", methods=["GET"])
def items_index():
    try:
        # Extract JWT token from the Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header:
            token = auth_header.split(" ")[1]  # Assuming Bearer token format
        else:
            return jsonify({"error": "Authentication token missing"}),  401

        # Decode the JWT token to get the user_id
        secret_key = app.config['SECRET_KEY']
        decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
        user_id = decoded_token['user_id']

        # Retrieve items associated with the user_id
        items_data = []
        for item in db.items_all_for_user(user_id):
            item_data = db.get_item_with_category_and_images(item["id"])
            if item_data:
                items_data.append(item_data)

        return jsonify(items_data)
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}),  401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}),  401
    except Exception as e:
        return jsonify({"error": str(e)}),  500

@app.route("/items.json", methods=["POST"])
def item_create():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]  # Remove 'Bearer ' prefix
            
            # Call the get_user_id_from_jwt function for debugging
            try:
                user_id = get_user_id_from_jwt(token)
                
                # Log the token after user ID extraction
                
                # Extract item data from the request form
                name = request.form.get("name")
                brand = request.form.get("brand")
                size = request.form.get("size")
                color = request.form.get("color")
                fit = request.form.get("fit")
                category_id = request.form.get("category_id")
                image = request.files.get("image")

                # Ensure that all required fields are provided
                if not (name and brand and size and color and fit and category_id):
                    raise ValueError("Missing required fields")

                # Save the image file to a secure location if provided
                if image:
                    filename = secure_filename(image.filename)
                    filepath = os.path.join('uploads', filename)
                    image.save(filepath)
                else:
                    filename = None
                    filepath = None

                # Create the item in the database
                db.items_create(name, brand, size, color, fit, category_id, filename, filepath, user_id)
                # If item creation was successful and an image was provided, associate the image with the item in the database
                # if item and image:
                #     db.images_create(filename, item["item_id"])

                return jsonify({"message": "Item created successfully"})
            except Exception as e:
                # Handle exceptions
                return jsonify({"error": str(e)}),   400
        else:
            return jsonify({"error": "Invalid Authorization header format"}),   401
    else:
        return jsonify({"error": "Authentication token missing"}),   401


@app.route("/items/<id>.json")
def item_show(id):
    try:
        item_data = db.get_item_with_category_and_images(id)
        if item_data:
            return jsonify(item_data)
        else:
            return jsonify({"error": "Item not found"}),  404
    except Exception as e:
        return jsonify({"error": str(e)}),  50


@app.route("/items/<id>.json", methods=["PATCH"])
def item_update(id):
    logger.debug(f"Received PATCH request for item ID: {id}")
    auth_header = request.headers.get('Authorization')
    if auth_header:
        token = auth_header.split(" ")[1]  # Assuming Bearer token format
    else:
        logger.warning("Authentication token missing")
        return jsonify({"error": "Authentication token missing"}),  401

    # Extract user_id from the JWT token
    user_id = get_user_id_from_jwt(token)
    try:
        
        name = request.form.get("name")
        brand = request.form.get("brand")
        size = request.form.get("size")
        color = request.form.get("color")
        fit = request.form.get("fit")
        category_id = request.form.get("category_id")

        image = request.files.get("image")
        # Call the items_update_by_id function with the provided parameters
        updated_item = db.items_update_by_id(id, name, brand, size, color, fit, category_id, image)
        
        if updated_item:
            return jsonify({"message": "Item updated successfully"})
        else:
            return jsonify({"error": "Failed to update item"}), 500
    except Exception as e:
        # Handle exceptions
        return jsonify({"error": str(e)}), 500


@app.route("/items/<id>.json", methods=["DELETE"])
def item_destroy(id):
    return db.items_destroy_by_id(id)


############################# CATEGORY ROUTES ######################

@app.route("/categories.json")
def category_index():
    return db.categories_all()


@app.route("/categories.json", methods=["POST"])
def category_create():
    category_name = request.form.get("category_name")
    return db.categories_create(category_name)

@app.route("/categories/<id>.json")
def category_show(id):
    return db.categories_find_by_id(id)


@app.route("/categories/<id>.json", methods=["PATCH"])
def category_update(id):
    category_name = request.form.get("category_name")
    return db.categories_update_by_id(id, category_name)

@app.route("/categories/<id>.json", methods=["DELETE"])
def category_destroy(id):
    return db.categories_destroy_by_id(id)



############################# USER ROUTES ######################

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data["id"]) if user_data else None
        self.email = user_data["email"] if user_data else None
    
    def __repr__(self):
        return f'<User id={self.id}, email={self.email}>'

@app.route("/users.json")
def users_index():
    users = db.get_all_users()
    return jsonify(users)

@login_manager.user_loader
def load_user(user_id):
    print(f"Loading User: {user_id}")
    user_data = db.get_user_by_id(user_id)
    return User(user_data) if user_data else None

@app.route("/signup", methods=["POST"])
def signup():
    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        return {"message": "Email and password are required"}, 400

    existing_user = db.get_user_by_email(email)
    if existing_user:
        return {"message": "Email already exists"}, 400

    db.create_user(email, password)
    return {"message": "User created successfully"}

def generate_jwt_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=1)  # Token expires in  1 day
    }
    secret_key = app.config['SECRET_KEY']
    return jwt.encode(payload, secret_key, algorithm='HS256')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.is_json:  # Check if the request is JSON
            data = request.get_json()
        else:  # If not JSON, try to get form data
            data = request.form.to_dict()

        email = data.get("email")
        password = data.get("password")

        user = db.get_user_by_email(email)

        if user and check_password(password, user["password"]):
            user_obj = User(user)
            # login_user(user_obj)  # Comment out this line if you're using JWT
            print(f"Current User: {user_obj}")
            
            token = generate_jwt_token(user_obj.id)
            response = make_response({"message": "Login successful", "token": token})
            print("Response headers:", dict(response.headers))
            
            return response  # No need to manually set the cookie
        else:
            return {"message": "Invalid email or password"},   401

    return render_template('login.html')



blacklisted_tokens = set()

@app.route("/logout", methods=["POST"])
def logout():
    token = request.headers.get('Authorization').split()[1]
    blacklisted_tokens.add(token)
    return jsonify({"message": "Logout successful"})

############################# IMAGES ROUTES ######################


logging.basicConfig(level=logging.INFO)

def allowed_file(filename):
    """Check if the given filename has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@app.route("/images.json")
def image_index():
    return db.images_all()

def image_create(filename, item_id):
    try:
        conn = connect_to_db()
        cursor = conn.execute(
            """
            INSERT INTO images (filename, filepath, item_id)
            VALUES (?, ?, ?)
            RETURNING *
            """,
            (filename, os.path.join('uploads', filename), item_id),
        )

        inserted_row = cursor.fetchone()
        conn.commit()
        return dict(inserted_row) if inserted_row else None
    except Exception as e:
        logging.error(f"Error inserting image into database: {e}")
        conn.rollback()  # Roll back the transaction in case of error
        return None
    finally:
        conn.close()


def get_item_with_category_and_images(item_id):
    conn = connect_to_db()
    cursor = conn.execute(
        """
        SELECT items.*, categories.category_name, images.filename, images.filepath
        FROM items
        JOIN categories ON items.category_id = categories.id
        LEFT JOIN images ON items.id = images.item_id
        WHERE items.id = ?
        """,
        (item_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        item_with_images = dict(row)
        # Remove the individual filename and filepath keys from the dictionary
        item_with_images.pop("filename", None)
        item_with_images.pop("filepath", None)
        return item_with_images
    else:
        return None


@app.route("/images/<id>.json", methods=["DELETE"])
def image_destroy(id):
    return db.images_destroy_by_id(id)

@app.route('/uploads/<path:filename>')
def serve_image(filename):
    logging.info("Serving image: %s", filename)
    # Assuming images are stored in a folder named 'uploads' in your project directory
    uploads_folder = 'uploads'
    return send_from_directory(os.path.abspath(uploads_folder), filename)