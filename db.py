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
        DROP TABLE IF EXISTS images;
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
    
    conn.execute(
        """
        CREATE TABLE images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            img_url TEXT,
            item_id INT,
            FOREIGN KEY (item_id) REFERENCES items (id)
        );
        """
    )

    
    
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
    
    images_seed_data = [
        ("https://www.birkenstock.com/on/demandware.static/-/Sites-master-catalog/default/dwb9806ae3/560771/560771_pair.jpg", 2),
    ]
    conn.executemany(
        """
        INSERT INTO images (img_url, item_id)
        VALUES (?,?)
        """,
        images_seed_data,
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
        SELECT items.id, items.name, items.brand, items.size, items.color, items.fit, items.category_id, images.img_url, categories.category_name
        FROM items
        LEFT JOIN images ON items.id = images.item_id
        LEFT JOIN categories ON items.category_id = categories.id
        """
    ).fetchall()
    return [{"id": row["id"], "name": row["name"], "brand": row["brand"], "size": row["size"], 
             "color": row["color"], "fit": row["fit"], "category_id": row["category_id"], 
             "category_name": row["category_name"], "img_url": row["img_url"]} for row in rows]



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

def get_item_with_category_and_images(item_id):
    conn = connect_to_db()
    cursor = conn.execute(
        """
        SELECT items.*, categories.category_name, GROUP_CONCAT(images.img_url) AS image_urls
        FROM items
        JOIN categories ON items.category_id = categories.id
        LEFT JOIN images ON items.id = images.item_id
        WHERE items.id = ?
        GROUP BY items.id
        """,
        (item_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        item_with_images = dict(row)
        item_with_images["image_urls"] = item_with_images["image_urls"].split(',') if item_with_images["image_urls"] else []
        return item_with_images
    else:
        return None


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


############################### IMAGES #########################

def images_all():
  conn = connect_to_db()
  rows = conn.execute(
      """
      SELECT * FROM images
      """
  ).fetchall()
  return [dict(row) for row in rows]

def images_create(img_url, item_id):
    conn = connect_to_db()
    row = conn.execute(
        """
        INSERT INTO images (img_url, item_id)
        VALUES (?, ?)
        RETURNING *
        """,
        (img_url, item_id),
    ).fetchone()
    conn.commit()
    return dict(row)

def images_destroy_by_id(id):
    conn = connect_to_db()
    row = conn.execute(
        """
        DELETE from images
        WHERE id = ?
        """,
        (id,)
    )
    conn.commit()
    return {"message": "Item destroyed successfully"}


