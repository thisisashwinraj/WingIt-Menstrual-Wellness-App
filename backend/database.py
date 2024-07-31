import math
import json
import bcrypt
import random
import string
import sqlite3
from datetime import datetime, timezone, timedelta


class CredentialsDB:
    def __init__(self, db_name="bin/flosql.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """
        )
        self.conn.commit()

    def add_credentials(self, username, password):
        cursor = self.conn.cursor()
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        cursor.execute(
            "INSERT INTO credentials (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )
        self.conn.commit()

    def update_password(self, username, new_password):
        cursor = self.conn.cursor()
        new_password_hash = bcrypt.hashpw(
            new_password.encode("utf-8"), bcrypt.gensalt()
        )

        cursor.execute(
            "UPDATE credentials SET password_hash = ? WHERE username = ?",
            (new_password_hash, username),
        )
        self.conn.commit()

    def verify_user(self, username, password):
        cursor = self.conn.cursor()

        cursor.execute(
            "SELECT password_hash FROM credentials WHERE username = ?", (username,)
        )
        result = cursor.fetchone()

        if result:
            stored_password_hash = result[0]

            if bcrypt.checkpw(password.encode("utf-8"), stored_password_hash):
                return True
            else:
                return False

        else:
            return None

    def delete_credentials(self, username):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM credentials WHERE username = ?", (username,))
        self.conn.commit()


class UserDB:
    def __init__(self, db_name="bin/flosql.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS User (
                userid TEXT PRIMARY KEY,
                name TEXT,
                dob TEXT,
                height REAL,
                weight REAL,
                phone TEXT,
                address TEXT,
                profile_pic_url TEXT,
                dietary_preferences TEXT,
                allergies TEXT,
                medical_conditions TEXT,
                avg_cycle_length INTEGER,
                avg_periods_length INTEGER
            )
        """
        )
        self.conn.commit()

    def add_user(
        self,
        userid,
        name,
        dob,
        height,
        weight,
        phone,
        address,
        profile_pic_url,
        dietary_preferences,
        allergies,
        medical_conditions,
        avg_cycle_length,
        avg_periods_length,
    ):
        cursor = self.conn.cursor()

        cursor.execute(
            """
            INSERT INTO User (userid, name, dob, height, weight, phone, address,
                              profile_pic_url, dietary_preferences, allergies,
                              medical_conditions, avg_cycle_length, avg_periods_length)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                userid,
                name,
                dob,
                height,
                weight,
                phone,
                address,
                profile_pic_url,
                dietary_preferences,
                allergies,
                medical_conditions,
                avg_cycle_length,
                avg_periods_length,
            ),
        )

        self.conn.commit()

    def edit_user(self, userid, **kwargs):
        cursor = self.conn.cursor()

        update_query = "UPDATE User SET "
        update_values = []

        for key, value in kwargs.items():
            update_query += f"{key} = ?, "
            update_values.append(value)

        update_query = update_query[:-2]
        update_query += " WHERE userid = ?"
        update_values.append(userid)

        cursor.execute(update_query, tuple(update_values))
        self.conn.commit()

    def get_user(self, userid):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM User WHERE userid = ?", (userid,))
        return cursor.fetchone()

    def delete_user(self, userid):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM User WHERE userid = ?", (userid,))
        self.conn.commit()

    def close_connection(self):
        self.conn.close()


class PeriodsDB:
    def __init__(self, db_name="bin/flosql.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Periods (
                periodsid INTEGER PRIMARY KEY AUTOINCREMENT,
                userid TEXT,
                start_date TEXT,
                end_date TEXT,
                flow_intensity INTEGER,
                notes TEXT,
                FOREIGN KEY (userid) REFERENCES User(userid),
                UNIQUE(userid, start_date)
            )
        """
        )
        self.conn.commit()

    def add_period(
        self, userid, start_date, end_date, flow_intensity="Medium", notes=""
    ):
        cursor = self.conn.cursor()

        cursor.execute(
            """
            INSERT INTO Periods (userid, start_date, end_date, flow_intensity, notes)
            VALUES (?, ?, ?, ?, ?)
        """,
            (userid, start_date, end_date, flow_intensity, notes),
        )

        self.conn.commit()
        period_id = cursor.lastrowid

        return period_id

    def edit_period(self, userid, start_date, **kwargs):
        cursor = self.conn.cursor()

        update_query = "UPDATE Periods SET "
        update_values = []

        for key, value in kwargs.items():
            update_query += f"{key} = ?, "
            update_values.append(value)

        update_query = update_query[:-2]
        update_query += " WHERE userid = ? AND start_date = ?"
        update_values.extend([userid, start_date])

        cursor.execute(update_query, tuple(update_values))
        self.conn.commit()

    def get_period(self, userid, start_date):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM Periods WHERE userid = ? AND start_date = ?",
            (userid, start_date),
        )
        return cursor.fetchone()

    def fetch_latest_periods(self, userid, count=10):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM Periods WHERE userid = ? ORDER BY start_date DESC LIMIT ?",
            (userid, count),
        )
        return cursor.fetchall()

    def delete_period(self, userid, start_date):
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM Periods WHERE userid = ? AND start_date = ?",
            (userid, start_date),
        )
        self.conn.commit()

    def delete_periods_for_user(self, userid):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM Periods WHERE userid = ?", (userid,))
        self.conn.commit()

    def close_connection(self):
        self.conn.close()


class CyclesDB:
    def __init__(self, db_name="bin/flosql.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Cycles (
                cycleid INTEGER PRIMARY KEY AUTOINCREMENT,
                start_date TEXT,
                end_date TEXT,
                cycle_length INTEGER,
                periodsid INTEGER,
                userid TEXT,
                FOREIGN KEY (periodsid) REFERENCES Periods(periodsid),
                FOREIGN KEY (userid) REFERENCES User(userid),
                UNIQUE(userid, start_date)
            )
        """
        )
        self.conn.commit()

    def add_cycle(self, start_date, end_date, periodsid, userid):
        cycle_length = (
            datetime.strptime(end_date, "%Y-%m-%d")
            - datetime.strptime(start_date, "%Y-%m-%d")
        ).days + 1
        cursor = self.conn.cursor()

        cursor.execute(
            """
            INSERT INTO Cycles (start_date, end_date, cycle_length, periodsid, userid)
            VALUES (?, ?, ?, ?, ?)
        """,
            (start_date, end_date, cycle_length, periodsid, userid),
        )

        self.conn.commit()

    def edit_cycle(self, userid, start_date, **kwargs):
        cursor = self.conn.cursor()

        update_query = "UPDATE Cycles SET "
        update_values = []

        for key, value in kwargs.items():
            update_query += f"{key} = ?, "
            update_values.append(value)

        update_query = update_query[:-2]
        update_query += " WHERE userid = ? AND start_date = ?"
        update_values.extend([userid, start_date])

        cursor.execute(update_query, tuple(update_values))
        self.conn.commit()

    def get_cycle(self, userid, start_date):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM Cycles WHERE userid = ? AND start_date = ?",
            (userid, start_date),
        )
        return cursor.fetchone()

    def fetch_latest_cycles(self, userid, count=10):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM Cycles WHERE userid = ? ORDER BY start_date DESC LIMIT ?",
            (userid, count),
        )
        return cursor.fetchall()

    def delete_cycle(self, userid, start_date):
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM Cycles WHERE userid = ? AND start_date = ?",
            (userid, start_date),
        )
        self.conn.commit()

    def delete_cycles_for_user(self, userid):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM Cycles WHERE userid = ?", (userid,))
        self.conn.commit()

    def close_connection(self):
        self.conn.close()


class SymptomsDB:
    def __init__(self, db_name="bin/flosql.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Symptoms (
                symptomsid INTEGER PRIMARY KEY AUTOINCREMENT,
                userid TEXT,
                date TEXT,
                physical_symptoms TEXT,
                energy_level INTEGER,
                sleep_quality INTEGER,
                emotional_symptoms TEXT,
                UNIQUE(userid, date)
            )
        """
        )
        self.conn.commit()

    def add_symptoms(
        self,
        userid,
        date,
        physical_symptoms="",
        energy_level="",
        sleep_quality="",
        emotional_symptoms="",
    ):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO Symptoms (userid, date, physical_symptoms, energy_level,
                                  sleep_quality, emotional_symptoms)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                userid,
                date,
                physical_symptoms,
                energy_level,
                sleep_quality,
                emotional_symptoms,
            ),
        )
        self.conn.commit()

    def edit_symptoms(self, userid, date, **kwargs):
        cursor = self.conn.cursor()

        update_query = "UPDATE Symptoms SET "
        update_values = []

        for key, value in kwargs.items():
            update_query += f"{key} = ?, "
            update_values.append(value)

        update_query = update_query[:-2]
        update_query += " WHERE userid = ? AND date = ?"
        update_values.extend([userid, date])

        cursor.execute(update_query, tuple(update_values))
        self.conn.commit()

    def get_symptoms(self, userid, date):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM Symptoms WHERE userid = ? AND date = ?", (userid, date)
        )
        return cursor.fetchone()

    def get_symptoms_between_two_dates(self, userid, start_date, end_date):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM Symptoms WHERE userid = ? AND date BETWEEN ? AND ?",
            (userid, start_date, end_date),
        )
        return cursor.fetchall()

    def delete_symptoms(self, userid, date):
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM Symptoms WHERE userid = ? AND date = ?", (userid, date)
        )
        self.conn.commit()

    def delete_symptoms_for_user(self, userid):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM Symptoms WHERE userid = ?", (userid,))
        self.conn.commit()

    def close_connection(self):
        self.conn.close()


class NotificationsDB:
    def __init__(self, db_name="bin/flosql.db"):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()

    def create_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS notifications (
            notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
            userid TEXT,
            date TEXT NOT NULL,
            message TEXT NOT NULL
        );
        """
        self.cursor.execute(create_table_query)
        self.connection.commit()

    def add_notification(self, userid, date, message):
        insert_query = """
        INSERT INTO notifications (userid, date, message)
        VALUES (?, ?, ?);
        """
        self.cursor.execute(insert_query, (userid, date, message))

        self.connection.commit()
        return self.cursor.lastrowid

    def fetch_notifications(self, limit=None):
        if limit:
            fetch_query = "SELECT * FROM notifications LIMIT ?;"
            self.cursor.execute(fetch_query, (limit,))

        else:
            fetch_query = "SELECT * FROM notifications;"
            self.cursor.execute(fetch_query)

        return self.cursor.fetchall()

    def fetch_notifications_for_user(self, userid, limit=None):
        if limit:
            fetch_query = 'SELECT * FROM notifications WHERE userid = ? OR userid = "all" ORDER BY notification_id DESC LIMIT ?;'
            self.cursor.execute(fetch_query, (userid, limit))

        else:
            fetch_query = 'SELECT * FROM notifications WHERE userid = ? OR userid = "all" ORDER BY notification_id DESC;'
            self.cursor.execute(fetch_query, (userid,))

        return self.cursor.fetchall()

    def delete_notifications_for_user(self, userid):
        self.cursor.execute("DELETE FROM notifications WHERE userid = ?", (userid,))
        self.conn.commit()

    def close(self):
        self.connection.close()


class PostsDB:
    def __init__(self, db_name="bin/flosql.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Posts (
                postid INTEGER PRIMARY KEY AUTOINCREMENT,
                userid TEXT,
                created_on TEXT,
                content TEXT,
                image_url TEXT,
                likes INTEGER DEFAULT 0,
                dislikes INTEGER DEFAULT 0,
                reports INTEGER DEFAULT 0,
                FOREIGN KEY (userid) REFERENCES User(userid)
            )
        """
        )
        self.conn.commit()

    def add_post(self, userid, content, image_url=None):
        created_on = datetime.now().strftime("%B %d, %Y at %H:%M")
        cursor = self.conn.cursor()

        cursor.execute(
            """
            INSERT INTO Posts (userid, created_on, content, image_url)
            VALUES (?, ?, ?, ?)
        """,
            (userid, created_on, content, image_url),
        )

        self.conn.commit()

    def edit_post(self, postid, **kwargs):
        cursor = self.conn.cursor()

        update_query = "UPDATE Posts SET "
        update_values = []

        for key, value in kwargs.items():
            update_query += f"{key} = ?, "
            update_values.append(value)

        update_query = update_query[:-2]
        update_query += " WHERE postid = ?"
        update_values.append(postid)

        cursor.execute(update_query, tuple(update_values))
        self.conn.commit()

    def get_post(self, postid):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Posts WHERE postid = ?", (postid,))
        return cursor.fetchone()

    def get_post_by_userid(self, userid):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM Posts WHERE userid = ? ORDER BY postid DESC", (userid,)
        )
        return cursor.fetchall()

    def increment_likes(self, postid):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE Posts SET likes = likes + 1 WHERE postid = ?", (postid,))
        self.conn.commit()

    def increment_dislikes(self, postid):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE Posts SET dislikes = dislikes + 1 WHERE postid = ?", (postid,)
        )
        self.conn.commit()

    def increment_reports(self, postid):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE Posts SET reports = reports + 1 WHERE postid = ?", (postid,)
        )
        self.conn.commit()

    def get_number_of_pages(self, posts_per_page=5):
        cursor = self.conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM Posts")
        total_posts = cursor.fetchone()[0]

        return total_posts

    def get_posts_for_given_range(self, page_number, posts_per_page=5):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Posts")
        total_posts = cursor.fetchone()[0]

        start_pos = total_posts - ((page_number - 1) * posts_per_page)
        end_pos = start_pos - posts_per_page + 1

        if start_pos > end_pos:
            start_pos, end_pos = end_pos, start_pos

        query = """
        SELECT * FROM (
            SELECT *, ROW_NUMBER() OVER (ORDER BY postid DESC) AS row_num
            FROM Posts
        ) WHERE row_num BETWEEN ? AND ?
        """

        cursor.execute(query, (start_pos, end_pos))
        posts = cursor.fetchall()
        return posts

    def get_top_five_creators(self):
        cursor = self.conn.cursor()

        query = """
        SELECT userid, COUNT(*) as post_count
        FROM Posts
        GROUP BY userid
        ORDER BY post_count DESC
        LIMIT 5
        """
        cursor.execute(query)

        top_creators = cursor.fetchall()
        return top_creators

    def get_total_likes_dislikes_reports_posts_count(self, userid):
        cursor = self.conn.cursor()

        query = """
            SELECT 
                SUM(likes) as total_likes, 
                SUM(dislikes) as total_dislikes, 
                SUM(reports) as total_reports, 
                COUNT(*) as total_posts
            FROM 
                Posts
            WHERE 
                userid = ?
        """
        cursor.execute(query, (userid,))

        stats = cursor.fetchone()
        return stats

    def delete_post(self, postid):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM Posts WHERE postid = ?", (postid,))
        self.conn.commit()

    def delete_posts_for_user(self, userid):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM Posts WHERE userid = ?", (userid,))
        self.conn.commit()

    def close_connection(self):
        self.conn.close()


class ProductsDB:
    def __init__(self, db_name="bin/flosql.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Products (
                productid INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                brand TEXT,
                description TEXT,
                type TEXT,
                price REAL,
                discount REAL,
                image TEXT,
                stock INTEGER
            )
        """
        )
        self.conn.commit()

    def add_product(
        self, name, brand, description, type, price, discount, image, stock
    ):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO Products (name, brand, description, type, price, discount, image, stock)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (name, brand, description, type, price, discount, image, stock),
        )
        self.conn.commit()

    def edit_product(self, productid, **kwargs):
        cursor = self.conn.cursor()

        update_query = "UPDATE Products SET "
        update_values = []

        for key, value in kwargs.items():
            update_query += f"{key} = ?, "
            update_values.append(value)

        update_query = update_query[:-2]
        update_query += " WHERE productid = ?"
        update_values.append(productid)

        cursor.execute(update_query, tuple(update_values))
        self.conn.commit()

    def get_product(self, productid):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Products WHERE productid = ?", (productid,))
        return cursor.fetchone()

    def get_number_of_products(self, filters=[]):
        cursor = self.conn.cursor()

        query = "SELECT COUNT(*) FROM Products WHERE 1=1"

        if "Products Under Rs.500" in filters:
            query += " AND price < 500"
        if "Sanitary Products" in filters:
            query += " AND type IN ('Pads', 'Tampons', 'Pantyliners', 'Sponges', 'Menstrual Cups', 'Menstrual Discs')"
        if "Minimum 15% Discount" in filters:
            query += " AND discount >= 15"
        if "Reusable Material" in filters:
            query += " AND type IN ('Menstrual Cups', 'Menstrual Discs', 'Menstrual Sponges')"
        if "Budget Friendly Items" in filters:
            query += " AND price < 300"

        cursor.execute(query)

        total_products = cursor.fetchone()[0]
        return total_products

    def get_products_for_given_range(
        self, page_number, products_per_page=12, selected_filters=[]
    ):
        cursor = self.conn.cursor()

        query = "SELECT COUNT(*) FROM Products WHERE 1=1"

        if "Products Under Rs.500" in selected_filters:
            query += " AND price < 500"
        if "Sanitary Products" in selected_filters:
            query += " AND type IN ('Pads', 'Tampons', 'Pantyliners', 'Sponges', 'Menstrual Cups', 'Menstrual Discs')"
        if "Minimum 15% Discount" in selected_filters:
            query += " AND discount >= 15"
        if "Reusable Material" in selected_filters:
            query += " AND type IN ('Menstrual Cups', 'Menstrual Discs', 'Menstrual Sponges')"
        if "Budget Friendly Items" in selected_filters:
            query += " AND price < 300"

        cursor.execute(query)
        total_products = cursor.fetchone()[0]

        start_pos = total_products - ((page_number - 1) * products_per_page)
        end_pos = start_pos - products_per_page + 1

        if start_pos > end_pos:
            start_pos, end_pos = end_pos, start_pos

        query = """
        SELECT * FROM (
            SELECT *, ROW_NUMBER() OVER (ORDER BY productid DESC) AS row_num
            FROM Products
            WHERE 1=1
        """

        if "Products Under Rs.500" in selected_filters:
            query += " AND price < 500"
        if "Sanitary Products" in selected_filters:
            query += " AND type IN ('Pads', 'Tampons', 'Pantyliners', 'Sponges', 'Menstrual Cups', 'Menstrual Discs')"
        if "Minimum 15% Discount" in selected_filters:
            query += " AND discount >= 15"
        if "Reusable Material" in selected_filters:
            query += " AND type IN ('Menstrual Cups', 'Menstrual Discs', 'Menstrual Sponges')"
        if "Budget Friendly Items" in selected_filters:
            query += " AND price < 300"

        query += """
        ) AS filtered_products 
        WHERE row_num BETWEEN ? AND ?
        """

        cursor.execute(query, (start_pos, end_pos))
        products = cursor.fetchall()
        return products

    def delete_product(self, productid):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM Products WHERE productid = ?", (productid,))
        self.conn.commit()

    def close_connection(self):
        self.conn.close()


class WishlistDB:
    def __init__(self, db_name="bin/flosql.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Wishlist (
                wishlistid INTEGER PRIMARY KEY AUTOINCREMENT,
                userid TEXT,
                productid INTEGER,
                added_on TEXT,
                FOREIGN KEY (userid) REFERENCES User(userid),
                FOREIGN KEY (productid) REFERENCES Products(productid)
            )
        """
        )
        self.conn.commit()

    def add_wishlist_item(self, userid, productid):
        added_on = datetime.now().strftime("%B %d, %Y at %H:%M")
        cursor = self.conn.cursor()

        cursor.execute(
            """
            INSERT INTO Wishlist (userid, productid, added_on)
            VALUES (?, ?, ?)
        """,
            (userid, productid, added_on),
        )

        self.conn.commit()

    def edit_wishlist_item(self, wishlistid, **kwargs):
        cursor = self.conn.cursor()

        update_query = "UPDATE Wishlist SET "
        update_values = []

        for key, value in kwargs.items():
            update_query += f"{key} = ?, "
            update_values.append(value)

        update_query = update_query[:-2]
        update_query += " WHERE wishlistid = ?"
        update_values.append(wishlistid)

        cursor.execute(update_query, tuple(update_values))
        self.conn.commit()

    def get_wishlist_by_userid(self, userid):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Wishlist WHERE userid = ?", (userid,))
        return cursor.fetchall()

    def get_wishlist_item(self, wishlistid):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Wishlist WHERE wishlistid = ?", (wishlistid,))
        return cursor.fetchone()

    def delete_wishlist_item(self, wishlistid):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM Wishlist WHERE wishlistid = ?", (wishlistid,))
        self.conn.commit()

    def remove_product_from_wishlist(self, productid, userid):
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM Wishlist WHERE productid = ? AND userid = ?",
            (productid, userid),
        )
        self.conn.commit()

    def delete_wishlist_for_user(self, userid):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM Wishlist WHERE userid = ?", (userid,))
        self.conn.commit()

    def close_connection(self):
        self.conn.close()


class CartDB:
    def __init__(self, db_name="bin/flosql.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Cart (
                cartid INTEGER PRIMARY KEY AUTOINCREMENT,
                userid TEXT,
                productid INTEGER,
                quantity INTEGER,
                FOREIGN KEY (userid) REFERENCES User(userid),
                FOREIGN KEY (productid) REFERENCES Products(productid)
            )
        """
        )
        self.conn.commit()

    def add_cart_item(self, userid, productid, quantity):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO Cart (userid, productid, quantity)
            VALUES (?, ?, ?)
        """,
            (userid, productid, quantity),
        )
        self.conn.commit()

    def edit_cart_item(self, cartid, **kwargs):
        cursor = self.conn.cursor()

        update_query = "UPDATE Cart SET "
        update_values = []

        for key, value in kwargs.items():
            update_query += f"{key} = ?, "
            update_values.append(value)

        update_query = update_query[:-2]
        update_query += " WHERE cartid = ?"
        update_values.append(cartid)

        cursor.execute(update_query, tuple(update_values))
        self.conn.commit()

    def get_cart_from_userid(self, userid):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Cart WHERE userid = ?", (userid,))
        return cursor.fetchall()

    def delete_cart_item(self, userid, productid):
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM Cart WHERE productid = ? AND userid = ?", (productid, userid)
        )
        self.conn.commit()

    def delete_cart_for_user(self, userid):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM Cart WHERE userid = ?", (userid,))
        self.conn.commit()

    def close_connection(self):
        self.conn.close()


class OrdersDB:
    def __init__(self, db_name="bin/flosql.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Orders (
                orderid INTEGER PRIMARY KEY AUTOINCREMENT,
                userid TEXT,
                productids TEXT,
                quantitys TEXT,
                total_amount REAL,
                delivery_address, TEXT,
                ordered_on TEXT,
                status TEXT,
                FOREIGN KEY (userid) REFERENCES User(userid)
            )
        """
        )
        self.conn.commit()

    def add_order(
        self,
        userid,
        productids,
        quantitys,
        total_amount,
        delivery_address,
        status="pending",
    ):
        ordered_on = datetime.now().strftime("%B %d, %Y at %H:%M")

        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO Orders (userid, productids, quantitys, total_amount, delivery_address, ordered_on, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                userid,
                ",".join(map(str, productids)),
                ",".join(map(str, quantitys)),
                total_amount,
                delivery_address,
                ordered_on,
                status,
            ),
        )

        self.conn.commit()

    def edit_order(self, orderid, **kwargs):
        cursor = self.conn.cursor()

        update_query = "UPDATE Orders SET "
        update_values = []

        for key, value in kwargs.items():
            update_query += f"{key} = ?, "
            update_values.append(value)

        update_query = update_query[:-2]
        update_query += " WHERE orderid = ?"
        update_values.append(orderid)

        cursor.execute(update_query, tuple(update_values))
        self.conn.commit()

    def get_order(self, orderid):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Orders WHERE orderid = ?", (orderid,))
        return cursor.fetchone()

    def get_order_for_userid(self, userid):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Orders WHERE userid = ?", (userid,))
        return cursor.fetchall()

    def get_orderid_for_userid(self, userid):
        cursor = self.conn.cursor()
        cursor.execute("SELECT orderid FROM Orders WHERE userid = ?", (userid,))
        orders = cursor.fetchall()
        return [item[0] for item in orders]

    def delete_order(self, orderid):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM Orders WHERE orderid = ?", (orderid,))
        self.conn.commit()

    def delete_orders_for_user(self, userid):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM Orders WHERE userid = ?", (userid,))
        self.conn.commit()

    def close_connection(self):
        self.conn.close()


class RatingsDB:
    def __init__(self, db_name="bin/flosql.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Ratings (
                ratingid INTEGER PRIMARY KEY AUTOINCREMENT,
                productid INTEGER,
                userid TEXT,
                rating REAL,
                rated_on TEXT,
                FOREIGN KEY (productid) REFERENCES Products(productid),
                FOREIGN KEY (userid) REFERENCES User(userid)
            )
        """
        )
        self.conn.commit()

    def add_rating(self, productid, userid, rating):
        rated_on = datetime.now().strftime("%B %d, %Y at %H:%M")
        cursor = self.conn.cursor()

        cursor.execute(
            """
            INSERT INTO Ratings (productid, userid, rating, rated_on)
            VALUES (?, ?, ?, ?)
        """,
            (productid, userid, rating, rated_on),
        )

        self.conn.commit()

    def edit_rating(self, ratingid, **kwargs):
        cursor = self.conn.cursor()

        update_query = "UPDATE Ratings SET "
        update_values = []

        for key, value in kwargs.items():
            update_query += f"{key} = ?, "
            update_values.append(value)

        update_query = update_query[:-2]
        update_query += " WHERE ratingid = ?"
        update_values.append(ratingid)

        cursor.execute(update_query, tuple(update_values))
        self.conn.commit()

    def get_rating(self, ratingid):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Ratings WHERE ratingid = ?", (ratingid,))
        return cursor.fetchone()

    def get_product_rating_info(self, productid):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT AVG(rating), COUNT(rating) FROM Ratings WHERE productid = ?",
            (productid,),
        )
        return cursor.fetchall()

    def delete_rating(self, ratingid):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM Ratings WHERE ratingid = ?", (ratingid,))
        self.conn.commit()

    def delete_ratings_for_user(self, userid):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM Ratings WHERE userid = ?", (userid,))
        self.conn.commit()

    def close_connection(self):
        self.conn.close()
