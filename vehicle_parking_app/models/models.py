import sqlite3
import os 

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIRECTORY)
DB_PATH = os.path.join(PROJECT_ROOT, 'database.db')

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("PRAGMA foreign_keys = ON")

# User Table
c.execute('''
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    full_name TEXT NOT NULL,
    address TEXT NOT NULL,
    pincode TEXT NOT NULL
)
''')

# Admin Table
c.execute('''
CREATE TABLE IF NOT EXISTS admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    full_name TEXT NOT NULL,
    address TEXT NOT NULL,
    pincode TEXT NOT NULL
)
''')


# Parking Lot Table
c.execute('''
CREATE TABLE parking_lot (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prime_location_name TEXT NOT NULL,
    address TEXT NOT NULL,
    pincode TEXT NOT NULL,
    price_per_hour REAL NOT NULL,
    max_spots INTEGER NOT NULL 
);
''')

# Parking Spot Table
c.execute('''
CREATE TABLE parking_spot (
    id INTEGER NOT NULL,
    lot_id INTEGER NOT NULL,
    is_occupied INTEGER DEFAULT 0,
    PRIMARY KEY (id, lot_id),
    FOREIGN KEY (lot_id) REFERENCES parking_lot(id)
);
''')

# Reservation Table
c.execute('''
CREATE TABLE reservation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    lot_id INTEGER NOT NULL,
    spot_id INTEGER NOT NULL,
    vehicle_no TEXT NOT NULL,
    date_of_parking TEXT NOT NULL,
    time_of_parking TEXT NOT NULL,
    parking_cost REAL NOT NULL,
    time_of_release TEXT,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (lot_id, spot_id) REFERENCES parking_spot(lot_id, id)
);
''')

conn.commit()
conn.close()