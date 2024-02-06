import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash


def connect_to_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


def initial_setup():
    conn = connect_to_db()
    conn.execute(
        """
        DROP TABLE IF EXISTS categories;
        """
    )
    conn.execute(
        """
        DROP TABLE IF EXISTS items;
        """
    )
    conn.execute(
        """
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT UNIQUE NOT NULL
        );
        """
    )
    conn.execute(
        """
        CREATE TABLE items (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT,
          brand TEXT,
          size TEXT,
          color TEXT,
          fit TEXT,
          category_id INT,
          FOREIGN KEY (category_id) REFERENCES categories (id)
        );
        """
    )
#     conn.execute(
#     """
#     CREATE TABLE users (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         email TEXT UNIQUE NOT NULL,
#         password TEXT NOT NULL
#     );
#     """
# )
    conn.commit()
    print("Tables created successfully")

    categories_seed_data = [
    ("Shirts",),
    ("Pants",),
    ("Sweaters",),
    ("Sweatpants",),
    ("Shoes",),
    ("Accessories",),
    ("Jackets",),
    ("Suits + Blazers",),
    ("Sneakers",)
    ]

    conn.executemany(
        """
        INSERT INTO categories (category_name)
        VALUES (?)
        """,
        categories_seed_data
    )
    conn.commit()
    print("Cateogry seed data created successfully")



    items_seed_data = [
        ("Loose-fit Jeans", "HOPE", 34, "Mid Grey Stone", "very baggy", 2),
    ]
    conn.executemany(
        """
        INSERT INTO items (name, brand, size, color, fit, category_id)
        VALUES (?,?,?,?,?,?)
        """,
        items_seed_data,
    )
    conn.commit()
    print("Seed data created successfully")

    conn.close()

def reset_items_table():
    conn = connect_to_db()
    conn.execute(
        """
        DROP TABLE IF EXISTS items;
        """
    )
    conn.execute(
        """
        CREATE TABLE items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            brand TEXT,
            size TEXT,  -- Change size column to TEXT
            color TEXT,
            fit TEXT,
            category_id INT,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        );
        """
    )
    conn.commit()
    print("Items table reset successfully")


if __name__ == "__main__":
    initial_setup()

############################### ITEMS #########################

def items_all():
  conn = connect_to_db()
  rows = conn.execute(
      """
      SELECT * FROM items
      """
  ).fetchall()
  return [{"id": row["id"], "name": row["name"], "brand": row["brand"], "size": row["size"], "color": row["color"], "fit": row["fit"], "category_id": row["category_id"]} for row in rows]


def items_create(name, brand, size, color, fit, category_id):
    conn = connect_to_db()
    row = conn.execute(
        """
        INSERT INTO items (name, brand, size, color, fit, category_id)
        VALUES (?, ?, ?, ?, ?, ?)
        RETURNING *
        """,
        (name, brand, size, color, fit, category_id),
    ).fetchone()
    conn.commit()
    return dict(row)

def items_find_by_id(id):
    conn = connect_to_db()
    row = conn.execute(
        """
        SELECT * FROM items
        WHERE id = ?
        """,
        id,
    ).fetchone()
    return dict(row)

def items_update_by_id(id, name, brand, size, color, fit, category_id):
    conn = connect_to_db()
    row = conn.execute(
        """
        UPDATE items SET name = ?, brand = ?, size = ?, color = ?, fit = ?, category_id = ? 
        WHERE id = ?
        RETURNING *
        """,
        (name, brand, size, color, fit, category_id, id),
    ).fetchone()
    conn.commit()
    return dict(row)

def items_destroy_by_id(id):
    conn = connect_to_db()
    row = conn.execute(
        """
        DELETE from items
        WHERE id = ?
        """,
        (id,)
    )
    conn.commit()
    return {"message": "Item destroyed successfully"}


############################### CATEGORIES #########################

def categories_all():
  conn = connect_to_db()
  rows = conn.execute(
      """
      SELECT * FROM categories
      """
  ).fetchall()
  return [dict(row) for row in rows]


def categories_create(category_name):
    conn = connect_to_db()
    row = conn.execute(
        """
        INSERT INTO categories (category_name)
        VALUES (?)
        RETURNING *
        """,
        (category_name,),
    ).fetchone()
    conn.commit()
    return dict(row)

def categories_find_by_id(id):
    conn = connect_to_db()
    row = conn.execute(
        """
        SELECT * FROM categories
        WHERE id = ?
        """,
        id,
    ).fetchone()
    return dict(row)

def categories_update_by_id(id, category_name):
    conn = connect_to_db()
    row = conn.execute(
        """
        UPDATE categories SET category_name = ? 
        WHERE id = ?
        RETURNING *
        """,
        (category_name, id),
    ).fetchone()
    conn.commit()
    return dict(row)

def categories_destroy_by_id(id):
    conn = connect_to_db()
    row = conn.execute(
        """
        DELETE from categories
        WHERE id = ?
        """,
        (id,),
    )
    conn.commit()
    return {"message": "Category destroyed successfully"}


############################### USERS #########################


def create_user(email, password):
    conn = connect_to_db()
    hashed_password = hash_password(password)
    row = conn.execute(
        """
        INSERT INTO users (email, password)
        VALUES (?, ?)
        RETURNING *
        """,
        (email, hashed_password),
    ).fetchone()
    conn.commit()
    return dict(row)

def get_user_by_email(email):
    conn = connect_to_db()
    row = conn.execute(
        """
        SELECT * FROM users
        WHERE email = ?
        """,
        (email,),
    ).fetchone()
    return dict(row) if row else None

def get_user_by_id(user_id):
    conn = connect_to_db()
    row = conn.execute(
        """
        SELECT * FROM users
        WHERE id = ?
        """,
        (user_id,),
    ).fetchone()
    return dict(row) if row else None


def hash_password(password):
    return generate_password_hash(password, method="pbkdf2:sha256")

def check_password(password, hashed_password):
    return check_password_hash(hashed_password, password)
