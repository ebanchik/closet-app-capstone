import db
from flask import Flask, request, jsonify, make_response, render_template
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from db import check_password
from decouple import config
from flask_cors import CORS

app = Flask(__name__)

secret_key = config("SECRET_KEY", default="default_secret_key")
app.secret_key = secret_key

CORS(app)

@app.route('/')
def home():
    if current_user.is_authenticated:
        return f'Hello, {current_user.email}! You are logged in.'
    else:
        return 'Hello, Guest!'

############################# ITEMS ROUTES #########################

@app.route("/items.json")
def items_index():
    return db.items_all()


@app.route("/items.json", methods=["POST"])
def item_create():
    item_name = request.form.get("item_name")
    return db.items_create(item_name)

@app.route("/items/<id>.json")
def item_show(id):
    return db.items_find_by_id(id)


@app.route("/items/<id>.json", methods=["PATCH"])
def item_update(id):
    name = request.form.get("name")
    brand = request.form.get("brand")
    size = request.form.get("size")
    color = request.form.get("color")
    fit = request.form.get("fit")
    item_id = request.form.get("item_id")
    return db.items_update_by_id(id, name, brand, size, color, fit, item_id)

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

login_manager = LoginManager(app)
login_manager.login_view = "login"

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
            login_user(user_obj)
            print(f"Current User: {current_user}")
            response = make_response({"message": "Login successful"})

            # Set the session cookie with the user's ID
            response.headers["Set-Cookie"] = f"user_id={current_user.id}; Path=/;"

            print("Headers:", response.headers)

            return response
        else:
            return {"message": "Invalid email or password"}, 401

    return render_template('login.html')


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return {"message": "Logout successful"}