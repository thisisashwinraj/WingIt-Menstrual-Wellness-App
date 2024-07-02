import json
import random
import string
import sqlite3
from datetime import datetime, timezone, timedelta


class UserDB:
    def __init__(self, db_name='bin/flosql.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
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
        ''')
        self.conn.commit()

    def add_user(self, userid, name, dob, height, weight, phone, address,
                 profile_pic_url, dietary_preferences, allergies, medical_conditions,
                 avg_cycle_length, avg_periods_length):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO User (userid, name, dob, height, weight, phone, address,
                              profile_pic_url, dietary_preferences, allergies,
                              medical_conditions, avg_cycle_length, avg_periods_length)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (userid, name, dob, height, weight, phone, address, profile_pic_url,
              dietary_preferences, allergies, medical_conditions, avg_cycle_length,
              avg_periods_length))
        self.conn.commit()

    def edit_user(self, userid, **kwargs):
        cursor = self.conn.cursor()
        update_query = 'UPDATE User SET '
        update_values = []
        for key, value in kwargs.items():
            update_query += f'{key} = ?, '
            update_values.append(value)
        # Remove the last comma and space
        update_query = update_query[:-2]
        update_query += ' WHERE userid = ?'
        update_values.append(userid)
        cursor.execute(update_query, tuple(update_values))
        self.conn.commit()

    def get_user(self, userid):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM User WHERE userid = ?', (userid,))
        return cursor.fetchone()

    def delete_user(self, userid):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM User WHERE userid = ?', (userid,))
        self.conn.commit()

    def close_connection(self):
        self.conn.close()


class PeriodsDB:
    def __init__(self, db_name='bin/flosql.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
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
        ''')
        self.conn.commit()

    def add_period(self, userid, start_date, end_date, flow_intensity, notes=''):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO Periods (userid, start_date, end_date, flow_intensity, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (userid, start_date, end_date, flow_intensity, notes))
        self.conn.commit()

    def edit_period(self, userid, start_date, **kwargs):
        cursor = self.conn.cursor()
        update_query = 'UPDATE Periods SET '
        update_values = []
        for key, value in kwargs.items():
            update_query += f'{key} = ?, '
            update_values.append(value)
        # Remove the last comma and space
        update_query = update_query[:-2]
        update_query += ' WHERE userid = ? AND start_date = ?'
        update_values.extend([userid, start_date])
        cursor.execute(update_query, tuple(update_values))
        self.conn.commit()

    def get_period(self, userid, start_date):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM Periods WHERE userid = ? AND start_date = ?', (userid, start_date))
        return cursor.fetchone()

    def delete_period(self, userid, start_date):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM Periods WHERE userid = ? AND start_date = ?', (userid, start_date))
        self.conn.commit()

    def close_connection(self):
        self.conn.close()


class CyclesDB:
    def __init__(self, db_name='bin/flosql.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
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
        ''')
        self.conn.commit()

    def add_cycle(self, start_date, end_date, periodsid, userid):
        cycle_length = (datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')).days
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO Cycles (start_date, end_date, cycle_length, periodsid, userid)
            VALUES (?, ?, ?, ?, ?)
        ''', (start_date, end_date, cycle_length, periodsid, userid))
        self.conn.commit()

    def edit_cycle(self, userid, start_date, **kwargs):
        cursor = self.conn.cursor()
        update_query = 'UPDATE Cycles SET '
        update_values = []
        for key, value in kwargs.items():
            update_query += f'{key} = ?, '
            update_values.append(value)
        # Remove the last comma and space
        update_query = update_query[:-2]
        update_query += ' WHERE userid = ? AND start_date = ?'
        update_values.extend([userid, start_date])
        cursor.execute(update_query, tuple(update_values))
        self.conn.commit()

    def get_cycle(self, userid, start_date):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM Cycles WHERE userid = ? AND start_date = ?', (userid, start_date))
        return cursor.fetchone()

    def delete_cycle(self, userid, start_date):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM Cycles WHERE userid = ? AND start_date = ?', (userid, start_date))
        self.conn.commit()

    def close_connection(self):
        self.conn.close()


class SymptomsDB:
    def __init__(self, db_name='bin/flosql.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
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
        ''')
        self.conn.commit()

    def add_symptoms(self, userid, date, physical_symptoms=None, energy_level=None,
                     sleep_quality=None, emotional_symptoms=None):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO Symptoms (userid, date, physical_symptoms, energy_level,
                                  sleep_quality, emotional_symptoms)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (userid, date, physical_symptoms, energy_level, sleep_quality, emotional_symptoms))
        self.conn.commit()

    def edit_symptoms(self, userid, date, **kwargs):
        cursor = self.conn.cursor()
        update_query = 'UPDATE Symptoms SET '
        update_values = []
        for key, value in kwargs.items():
            update_query += f'{key} = ?, '
            update_values.append(value)
        # Remove the last comma and space
        update_query = update_query[:-2]
        update_query += ' WHERE userid = ? AND date = ?'
        update_values.extend([userid, date])
        cursor.execute(update_query, tuple(update_values))
        self.conn.commit()

    def get_symptoms(self, userid, date):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM Symptoms WHERE userid = ? AND date = ?', (userid, date))
        return cursor.fetchone()

    def delete_symptoms(self, userid, date):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM Symptoms WHERE userid = ? AND date = ?', (userid, date))
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
            fetch_query = 'SELECT * FROM notifications WHERE userid = ? OR userid = "all" ORDER BY date DESC LIMIT ?;'
            self.cursor.execute(fetch_query, (userid, limit))
        else:
            fetch_query = 'SELECT * FROM notifications WHERE userid = ? OR userid = "all" ORDER BY date DESC;'
            self.cursor.execute(fetch_query, (userid,))

        return self.cursor.fetchall()

    def close(self):
        self.connection.close()


class PostsDB:
    def __init__(self, db_name='bin/flosql.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
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
        ''')
        self.conn.commit()

    def add_post(self, userid, content, image_url=None):
        created_on = datetime.now().strftime('%B %d, %Y at %H:%M')
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO Posts (userid, created_on, content, image_url)
            VALUES (?, ?, ?, ?)
        ''', (userid, created_on, content, image_url))
        self.conn.commit()

    def edit_post(self, postid, **kwargs):
        cursor = self.conn.cursor()
        update_query = 'UPDATE Posts SET '
        update_values = []
        for key, value in kwargs.items():
            update_query += f'{key} = ?, '
            update_values.append(value)
        # Remove the last comma and space
        update_query = update_query[:-2]
        update_query += ' WHERE postid = ?'
        update_values.append(postid)
        cursor.execute(update_query, tuple(update_values))
        self.conn.commit()

    def get_post(self, postid):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM Posts WHERE postid = ?', (postid,))
        return cursor.fetchone()

    def increment_likes(self, postid):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE Posts SET likes = likes + 1 WHERE postid = ?', (postid,))
        self.conn.commit()

    def increment_dislikes(self, postid):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE Posts SET dislikes = dislikes + 1 WHERE postid = ?', (postid,))
        self.conn.commit()

    def increment_reports(self, postid):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE Posts SET reports = reports + 1 WHERE postid = ?', (postid,))
        self.conn.commit()

    def delete_post(self, postid):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM Posts WHERE postid = ?', (postid,))
        self.conn.commit()

    def close_connection(self):
        self.conn.close()


class ProductsDB:
    def __init__(self, db_name='bin/flosql.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
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
        ''')
        self.conn.commit()

    def add_product(self, name, brand, description, type, price, discount, image, stock):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO Products (name, brand, description, type, price, discount, image, stock)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, brand, description, type, price, discount, image, stock))
        self.conn.commit()

    def edit_product(self, productid, **kwargs):
        cursor = self.conn.cursor()
        update_query = 'UPDATE Products SET '
        update_values = []
        for key, value in kwargs.items():
            update_query += f'{key} = ?, '
            update_values.append(value)
        # Remove the last comma and space
        update_query = update_query[:-2]
        update_query += ' WHERE productid = ?'
        update_values.append(productid)
        cursor.execute(update_query, tuple(update_values))
        self.conn.commit()

    def get_product(self, productid):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM Products WHERE productid = ?', (productid,))
        return cursor.fetchone()

    def delete_product(self, productid):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM Products WHERE productid = ?', (productid,))
        self.conn.commit()

    def close_connection(self):
        self.conn.close()


class WishlistDB:
    def __init__(self, db_name='bin/flosql.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Wishlist (
                wishlistid INTEGER PRIMARY KEY AUTOINCREMENT,
                userid TEXT,
                productid INTEGER,
                added_on TEXT,
                FOREIGN KEY (userid) REFERENCES User(userid),
                FOREIGN KEY (productid) REFERENCES Products(productid)
            )
        ''')
        self.conn.commit()

    def add_wishlist_item(self, userid, productid):
        added_on = datetime.now().strftime('%B %d, %Y at %H:%M')
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO Wishlist (userid, productid, added_on)
            VALUES (?, ?, ?)
        ''', (userid, productid, added_on))
        self.conn.commit()

    def edit_wishlist_item(self, wishlistid, **kwargs):
        cursor = self.conn.cursor()
        update_query = 'UPDATE Wishlist SET '
        update_values = []
        for key, value in kwargs.items():
            update_query += f'{key} = ?, '
            update_values.append(value)
        # Remove the last comma and space
        update_query = update_query[:-2]
        update_query += ' WHERE wishlistid = ?'
        update_values.append(wishlistid)
        cursor.execute(update_query, tuple(update_values))
        self.conn.commit()

    def get_wishlist_item(self, wishlistid):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM Wishlist WHERE wishlistid = ?', (wishlistid,))
        return cursor.fetchone()

    def delete_wishlist_item(self, wishlistid):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM Wishlist WHERE wishlistid = ?', (wishlistid,))
        self.conn.commit()

    def close_connection(self):
        self.conn.close()


class CartDB:
    def __init__(self, db_name='bin/flosql.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Cart (
                cartid INTEGER PRIMARY KEY AUTOINCREMENT,
                userid TEXT,
                productid INTEGER,
                quantity INTEGER,
                FOREIGN KEY (userid) REFERENCES User(userid),
                FOREIGN KEY (productid) REFERENCES Products(productid)
            )
        ''')
        self.conn.commit()

    def add_cart_item(self, userid, productid, quantity):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO Cart (userid, productid, quantity)
            VALUES (?, ?, ?)
        ''', (userid, productid, quantity))
        self.conn.commit()

    def edit_cart_item(self, cartid, **kwargs):
        cursor = self.conn.cursor()
        update_query = 'UPDATE Cart SET '
        update_values = []
        for key, value in kwargs.items():
            update_query += f'{key} = ?, '
            update_values.append(value)
        # Remove the last comma and space
        update_query = update_query[:-2]
        update_query += ' WHERE cartid = ?'
        update_values.append(cartid)
        cursor.execute(update_query, tuple(update_values))
        self.conn.commit()

    def get_cart_item(self, cartid):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM Cart WHERE cartid = ?', (cartid,))
        return cursor.fetchone()

    def delete_cart_item(self, cartid):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM Cart WHERE cartid = ?', (cartid,))
        self.conn.commit()

    def close_connection(self):
        self.conn.close()


class OrdersDB:
    def __init__(self, db_name='bin/flosql.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Orders (
                orderid INTEGER PRIMARY KEY AUTOINCREMENT,
                userid TEXT,
                productids TEXT,
                quantitys TEXT,
                total_amount REAL,
                ordered_on TEXT,
                status TEXT,
                FOREIGN KEY (userid) REFERENCES User(userid)
            )
        ''')
        self.conn.commit()

    def add_order(self, userid, productids, quantitys, total_amount, status='pending'):
        ordered_on = datetime.now().strftime('%B %d, %Y at %H:%M')
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO Orders (userid, productids, quantitys, total_amount, ordered_on, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (userid, ','.join(map(str, productids)), ','.join(map(str, quantitys)), total_amount, ordered_on, status))
        self.conn.commit()

    def edit_order(self, orderid, **kwargs):
        cursor = self.conn.cursor()
        update_query = 'UPDATE Orders SET '
        update_values = []
        for key, value in kwargs.items():
            update_query += f'{key} = ?, '
            update_values.append(value)
        # Remove the last comma and space
        update_query = update_query[:-2]
        update_query += ' WHERE orderid = ?'
        update_values.append(orderid)
        cursor.execute(update_query, tuple(update_values))
        self.conn.commit()

    def get_order(self, orderid):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM Orders WHERE orderid = ?', (orderid,))
        return cursor.fetchone()

    def delete_order(self, orderid):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM Orders WHERE orderid = ?', (orderid,))
        self.conn.commit()

    def close_connection(self):
        self.conn.close()


class RatingsDB:
    def __init__(self, db_name='bin/flosql.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Ratings (
                ratingid INTEGER PRIMARY KEY AUTOINCREMENT,
                productid INTEGER,
                userid TEXT,
                rating REAL,
                rated_on TEXT,
                FOREIGN KEY (productid) REFERENCES Products(productid),
                FOREIGN KEY (userid) REFERENCES User(userid)
            )
        ''')
        self.conn.commit()

    def add_rating(self, productid, userid, rating):
        rated_on = datetime.now().strftime('%B %d, %Y at %H:%M')
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO Ratings (productid, userid, rating, rated_on)
            VALUES (?, ?, ?, ?)
        ''', (productid, userid, rating, rated_on))
        self.conn.commit()

    def edit_rating(self, ratingid, **kwargs):
        cursor = self.conn.cursor()
        update_query = 'UPDATE Ratings SET '
        update_values = []
        for key, value in kwargs.items():
            update_query += f'{key} = ?, '
            update_values.append(value)
        # Remove the last comma and space
        update_query = update_query[:-2]
        update_query += ' WHERE ratingid = ?'
        update_values.append(ratingid)
        cursor.execute(update_query, tuple(update_values))
        self.conn.commit()

    def get_rating(self, ratingid):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM Ratings WHERE ratingid = ?', (ratingid,))
        return cursor.fetchone()

    def delete_rating(self, ratingid):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM Ratings WHERE ratingid = ?', (ratingid,))
        self.conn.commit()

    def close_connection(self):
        self.conn.close()


if __name__ == '__main__':
    """
    db = UserDB()

    # Adding a user
    db.add_user('testuser', 'Alice', '1990-01-01', 165.0, 55.5, '+1234567890',
                '123 Main St, City, Country', 'http://example.com/alice.jpg',
                'Vegetarian', 'Peanuts', 'None', 28, 5)

    # Editing a user
    db.edit_user('testuser', name='User', weight=57.0)

    # Retrieving a user
    user = db.get_user('testuser')
    print(user)

    # Deleting a user
    db.delete_user('user001')

    db.close_connection()

    ##########################################################################

    db = PeriodsDB()

    # Adding a period
    db.add_period('user001', '2024-06-01', '2024-06-07', 2, 'Light flow')

    # Editing a period
    db.edit_period('user001', '2024-06-01', notes='Moderate flow')

    # Retrieving a period
    period = db.get_period('user001', '2024-06-01')
    print(period)

    # Deleting a period
    db.delete_period('user001', '2024-06-01')

    db.close_connection()

    ##########################################################################

    db = CyclesDB()

    # Adding a cycle
    db.add_cycle('2024-05-01', '2024-05-28', 1, 'user001')

    # Editing a cycle
    db.edit_cycle('user001', '2024-05-01', end_date='2024-05-29')

    # Retrieving a cycle
    cycle = db.get_cycle('user001', '2024-05-01')
    print(cycle)

    # Deleting a cycle
    db.delete_cycle('user001', '2024-05-01')

    db.close_connection()

    ##########################################################################

    db = SymptomsDB()

    # Adding symptoms
    db.add_symptoms('user001', '2024-07-01', physical_symptoms='Headache, Fatigue',
                    energy_level=3, sleep_quality=2, emotional_symptoms='Irritability')

    # Editing symptoms
    db.edit_symptoms('user001', '2024-07-01', energy_level=4)

    # Retrieving symptoms
    symptoms = db.get_symptoms('user001', '2024-07-01')
    print(symptoms)

    # Deleting symptoms
    db.delete_symptoms('user001', '2024-07-01')

    db.close_connection()
    
    ##########################################################################
    
    db = PostsDB()

    # Adding a post
    ans = db.add_post('user002', 'This is a post content.', 'http://example.com/image.jpg')

    # Incrementing likes, dislikes, and reports
    db.increment_likes(1)
    db.increment_dislikes(1)
    db.increment_reports(1)

    # Retrieving a post
    post = db.get_post(2)
    print(post)

    # Editing a post
    db.edit_post(1, content='This is an edited post content.')
    db.delete_post(1)

    db.close_connection()

    ##########################################################################

    db = ProductsDB()

    # Adding a product
    db.add_product('Sample Product', 'Sample Brand', 'This is a sample product description.',
                   'Sample Type', 99.99, 10.0, 'http://example.com/image.jpg', 100)

    # Editing a product
    db.edit_product(1, price=89.99, stock=150)

    # Retrieving a product
    product = db.get_product(1)
    print(product)

    # Deleting a product
    db.delete_product(1)

    db.close_connection()

    ##########################################################################

    db = WishlistDB()

    # Adding a wishlist item
    db.add_wishlist_item('user001', 1)

    # Editing a wishlist item
    db.edit_wishlist_item(1, productid=2)

    # Retrieving a wishlist item
    wishlist_item = db.get_wishlist_item(1)
    print(wishlist_item)

    # Deleting a wishlist item
    db.delete_wishlist_item(1)

    db.close_connection()

    ##########################################################################

    db = CartDB()

    # Adding a cart item
    db.add_cart_item('user001', 1, 2)

    # Editing a cart item
    db.edit_cart_item(1, quantity=3)

    # Retrieving a cart item
    cart_item = db.get_cart_item(1)
    print(cart_item)

    # Deleting a cart item
    db.delete_cart_item(1)

    db.close_connection()

    ##########################################################################
    
    db = OrdersDB()

    # Adding an order
    db.add_order('user001', [1, 2, 3], [1, 2, 1], 150.00)

    # Editing an order
    db.edit_order(1, status='shipped')

    # Retrieving an order
    order = db.get_order(1)
    print(order)

    # Deleting an order
    db.delete_order(1)

    db.close_connection()

    ##########################################################################

    db = RatingsDB()

    # Adding a rating
    db.add_rating(1, 'user001', 4.5)

    # Editing a rating
    db.edit_rating(1, rating=5.0)

    # Retrieving a rating
    rating = db.get_rating(1)
    print(rating)

    # Deleting a rating
    db.delete_rating(1)

    db.close_connection()

    ##########################################################################
    """
