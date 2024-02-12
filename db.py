import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from werkzeug.utils import secure_filename
import os
import jwt
from datetime import datetime, timedelta
from auth import get_user_id_from_jwt


def connect_to_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


def initial_setup():
    conn = connect_to_db()
    # conn.execute(
    #     """
    #     DROP TABLE IF EXISTS images
    #     """
    # )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT UNIQUE NOT NULL
        );
        """
    )
    # conn.execute("ALTER TABLE items RENAME TO items_old;")

# Step  2: Create a new table with the foreign key constraint
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            brand TEXT,
            size TEXT,
            color TEXT,
            fit TEXT,
            category_id INT,
            user_id INT,
            FOREIGN KEY (category_id) REFERENCES categories (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        """
    )

    # Step  3: Copy the data from the old table to the new table
    # conn.execute(
    #     """
    #     INSERT INTO items (id, name, brand, size, color, fit, category_id)
    #     SELECT id, name, brand, size, color, fit, category_id FROM items_old;
    #     """
    # )

    # Step  4: Drop the old table
    conn.execute("DROP TABLE items_old;")
#     conn.execute(
#     """
#     CREATE TABLE users (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         email TEXT UNIQUE NOT NULL,
#         password TEXT NOT NULL
#     );
#     """
# )
    
    # conn.execute(
    #     """
    #     CREATE TABLE images (
    #        id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         filename TEXT,
    #         filepath TEXT,
    #         item_id INT,
    #         FOREIGN KEY (item_id) REFERENCES items (id)
    #   );
    #     """
    # )

    conn.execute(
      """
      ALTER TABLE IF NOT users
      ADD COLUMN new_column_name column_type;
      """
    )

    
    
    conn.commit()
    print("Tables created successfully")

    # categories_seed_data = [
    # ("Shirts",),
    # ("Pants",),
    # ("Sweaters",),
    # ("Sweatpants",),
    # ("Shoes",),
    # ("Accessories",),
    # ("Jackets",),
    # ("Suits + Blazers",),
    # ("Sneakers",)
    # ]

    # conn.executemany(
    #     """
    #     INSERT INTO categories (category_name)
    #     VALUES (?)
    #     """,
    #     categories_seed_data
    # )
    # conn.commit()
    # print("Cateogry seed data created successfully")



    # items_seed_data = [
    #     ("Loose-fit Jeans", "HOPE", 34, "Mid Grey Stone", "very baggy", 2),
    # ]
    # conn.executemany(
    #     """
    #     INSERT INTO items (name, brand, size, color, fit, category_id)
    #     VALUES (?,?,?,?,?,?)
    #     """,
    #     items_seed_data,
    # )
    # conn.commit()
    # print("Seed data created successfully")
    
    # images_seed_data = [
    #     ("https://www.birkenstock.com/on/demandware.static/-/Sites-master-catalog/default/dwb9806ae3/560771/560771_pair.jpg", 2),
    # ]
    # conn.executemany(
    #     """
    #     INSERT INTO images (filename, filepath, item_id) VALUES (?,?,?);"
    #     """,
    #     images_seed_data,
    # )
    # conn.commit()
    # print("Seed data created successfully")

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
        SELECT items.id, items.name, items.brand, items.size, items.color, items.fit, items.category_id, categories.category_name,
               GROUP_CONCAT(images.filepath) AS filepaths
        FROM items
        LEFT JOIN categories ON items.category_id = categories.id
        LEFT JOIN images ON items.id = images.item_id
        GROUP BY items.id
        """
    ).fetchall()
    return [{"id": row["id"], "name": row["name"], "brand": row["brand"], "size": row["size"], "color": row["color"], "fit": row["fit"], "category_id": row["category_id"], "category_name": row["category_name"], "filepaths": row["filepaths"].split(',') if row["filepaths"] else []} for row in rows]

def items_all_for_user(user_id):
    conn = connect_to_db()
    # Create a cursor object
    cursor = conn.cursor()

    # Write the SQL query to select items for the given user_id
    sql = "SELECT * FROM items WHERE user_id = ?"

    # Execute the query with the user_id parameter
    cursor.execute(sql, (user_id,))

    # Fetch all results and close the cursor
    items = cursor.fetchall()
    cursor.close()

    return items




def items_create(name, brand, size, color, fit, category_id, image, token):
    user_id = get_user_id_from_jwt(token)
    logging.info('Creating item with parameters: name=%s, brand=%s, size=%s, color=%s, fit=%s, category_id=%s',
                 name, brand, size, color, fit, category_id)
    logging.info('Incoming image file: %s', image.filename if image else 'None')
    conn = connect_to_db()
    try:
        # Insert item data into the items table
        cursor = conn.execute(
            """
            INSERT INTO items (name, brand, size, color, fit, category_id)
            VALUES (?, ?, ?, ?, ?, ?)
            RETURNING id
            """,
            (name, brand, size, color, fit, category_id),
        )
        item_id = cursor.fetchone()[0]

        # Insert image data into the images table
        cursor = conn.execute(
            """
            INSERT INTO images (filename, filepath, item_id)
            VALUES (?, ?, ?)
            RETURNING *
            """,
            (secure_filename(image.filename), "upload/", item_id),
        )
        inserted_image = cursor.fetchone()

        conn.commit()
        return {"item_id": item_id, "image": dict(inserted_image)} if inserted_image else None
    except Exception as e:
        # Log the full stack trace for better debugging
        logging.exception("Error creating item: %s", e)
        
        # Return a more informative error message
        return {"error": f"An error occurred while creating the item: {str(e)}"}
    finally:
        # Only close the connection if it's open
        if conn:
            conn.close()

def items_find_by_id(id):
    conn = connect_to_db()
    row = conn.execute(
        """
        SELECT * FROM items
        WHERE id = ?
        """,
        (id,),
    ).fetchone()
    return dict(row)

def items_update_by_id(id, name, brand, size, color, fit, category_id, image):
    conn = connect_to_db()
    try:
        # Begin a transaction
        conn.execute("BEGIN TRANSACTION;")
        
        # Update item details in the items table
        conn.execute(
            """
            UPDATE items 
            SET name = ?, brand = ?, size = ?, color = ?, fit = ?, category_id = ?
            WHERE id = ?
            """,
            (name, brand, size, color, fit, category_id, id),
        )

        # If a new image is provided, update or add it to the images table
        if image:
            filename = secure_filename(image.filename)
            filepath = os.path.join('uploads', filename)
            image.save(filepath)
            conn.execute(
                """
                INSERT OR REPLACE INTO images (filename, filepath, item_id)
                VALUES (?, ?, ?)
                """,
                (filename, filepath, id),
            )

        # Commit the transaction
        conn.execute("COMMIT;")
        
        # Fetch and return the updated item details
        updated_row = conn.execute(
            """
            SELECT * FROM items
            WHERE id = ?
            """,
            (id,),
        ).fetchone()
        
        return dict(updated_row)
    except Exception as e:
        # Rollback the transaction in case of any error
        conn.execute("ROLLBACK;")
        # Log the error for debugging purposes
        logging.error(f"Error updating item: {e}")
        # Return None to indicate failure
        return None
    finally:
        # Close the database connection
        conn.close()

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
        SELECT items.*, categories.category_name, GROUP_CONCAT(images.filename) AS filenames, GROUP_CONCAT(images.filepath) AS filepaths
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
        item_with_images["filenames"] = item_with_images["filenames"].split(',') if item_with_images["filenames"] else []
        item_with_images["filepaths"] = item_with_images["filepaths"].split(',') if item_with_images["filepaths"] else []
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

def images_create(filename, filepath, item_id):
    try:
        conn = connect_to_db()
        cursor = conn.execute(
            """
            INSERT INTO images (filename, filepath, item_id)
            VALUES (?, ?, ?)
            RETURNING *
            """,
            (filename, filepath, item_id),
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

# def update_table():
#     conn = connect_to_db()
#     try:
#         # Add two new columns
#         conn.execute(
#             """
#             ALTER TABLE images
#             ADD COLUMN filename TEXT,
#             ADD COLUMN filepath TEXT;
#             """
#         )
        
#         # Drop the existing column
#         conn.execute(
#             """
#             ALTER TABLE images
#             DROP COLUMN img_url;
#             """
#         )

#         conn.commit()
#         print("Table updated successfully")
#     except sqlite3.Error as e:
#         print("Error updating table:", e)
#     finally:
#         conn.close()


