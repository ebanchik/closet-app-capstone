import db
from flask import Flask, request

app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello, World!'


@app.route("/items.json")
def index():
    return db.items_all()


@app.route("/items.json", methods=["POST"])
def create():
    name = request.form.get("name")
    brand = request.form.get("brand")
    size = request.form.get("size")
    color = request.form.get("color")
    fit = request.form.get("fit")
    category_id = request.form.get("category_id")
    return db.items_create(name, brand, size, color, fit, category_id)

@app.route("/items/<id>.json")
def show(id):
    return db.items_find_by_id(id)


@app.route("/items/<id>.json", methods=["PATCH"])
def update(id):
    name = request.form.get("name")
    brand = request.form.get("brand")
    size = request.form.get("size")
    color = request.form.get("color")
    fit = request.form.get("fit")
    category_id = request.form.get("category_id")
    return db.items_update_by_id(id, name, brand, size, color, fit, category_id)