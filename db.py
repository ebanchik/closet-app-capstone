import sqlite3


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
          size INT,
          color TEXT,
          fit TEXT,
          category_id INT,
          FOREIGN KEY (category_id) REFERENCES categories (id)
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

    conn.close()


if __name__ == "__main__":
    initial_setup()



def items_all():
  conn = connect_to_db()
  rows = conn.execute(
      """
      SELECT * FROM items
      """
  ).fetchall()
  return [dict(row) for row in rows]