import sqlite3
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
db_path = os.path.join(project_root, 'database.db')

conn = sqlite3.connect(db_path)
c = conn.cursor()

users = [
    ('user1@gmail.com', 'pass1', 'User One', 'Address 1', '111111'),
    ('user2@gmail.com', 'pass2', 'User Two', 'Address 2', '222222'),
    ('user3@gmail.com', 'pass3', 'User Three', 'Address 3', '333333'),
    ('user4@gmail.com', 'pass4', 'User Four', 'Address 4', '444444'),
    ('user5@gmail.com', 'pass5', 'User Five', 'Address 5', '555555')
]
for i in users:
    c.execute("insert into user (email, password, full_name, address, pincode) values (?, ?, ?, ?, ?)",i)

admins = [
    ('admin1@example.com', 'adminpass1', 'Admin One', 'Address 1', '111111'),
    ('admin2@example.com', 'adminpass2', 'Admin Two', 'Address 2', '222222'),
    ('admin3@example.com', 'adminpass3', 'Admin Three', 'Address 3', '333333'),
    ('admin4@example.com', 'adminpass4', 'Admin Four', 'Address 4', '444444'),
    ('admin5@example.com', 'adminpass5', 'Admin Five', 'Address 5', '555555')
]
for i in admins:
    c.execute("insert into admin (email, password, full_name, address, pincode) values (?, ?, ?, ?, ?)",i)

parkinglots = [
    ('Location A', 'Address 1', '111111', 15.00, 15),
    ('Location B', 'Address 2', '222222', 12.00, 20),
    ('Location C', 'Address 3', '333333', 10.00, 10),
    ('Location D', 'Address 4', '444444', 20.00, 13),
    ('Location E', 'Address 5', '555555', 18.00, 17)
]
for i in parkinglots:
    c.execute("INSERT INTO parking_lot (prime_location_name, address, pincode, price_per_hour, max_spots) VALUES (?, ?, ?, ?, ?)",i)

parkingspots = [
    (1, 1, 0), (2, 1, 0), (3, 1, 0), (4, 1, 0), (5, 1, 0),
    (6, 1, 0), (7, 1, 0), (8, 1, 0), (9, 1, 0), (10, 1, 0),
    (11, 1, 0), (12, 1, 0), (13, 1, 0), (14, 1, 0), (15, 1, 0),

    (1, 2, 0), (2, 2, 0), (3, 2, 0), (4, 2, 0), (5, 2, 0),
    (6, 2, 0), (7, 2, 0), (8, 2, 0), (9, 2, 0), (10, 2, 0),
    (11, 2, 0), (12, 2, 0), (13, 2, 0), (14, 2, 0), (15, 2, 0),
    (16, 2, 0), (17, 2, 0), (18, 2, 0), (19, 2, 0), (20, 2, 0),

    (1, 3, 0), (2, 3, 0), (3, 3, 0), (4, 3, 0), (5, 3, 0),
    (6, 3, 0), (7, 3, 0), (8, 3, 0), (9, 3, 0), (10, 3, 0),

    (1, 4, 0), (2, 4, 0), (3, 4, 0), (4, 4, 0), (5, 4, 0),
    (6, 4, 0), (7, 4, 0), (8, 4, 0), (9, 4, 0), (10, 4, 0),
    (11, 4, 0), (12, 4, 0), (13, 4, 0),

    (1, 5, 0), (2, 5, 0), (3, 5, 0), (4, 5, 0), (5, 5, 0),
    (6, 5, 0), (7, 5, 0), (8, 5, 0), (9, 5, 0), (10, 5, 0),
    (11, 5, 0), (12, 5, 0), (13, 5, 0), (14, 5, 0), (15, 5, 0),
    (16, 5, 0), (17, 5, 0)
]
for i in parkingspots:
    c.execute("INSERT INTO parking_spot (id, lot_id, is_occupied) values (?, ?, ?)",i)

reservations = [
    (1, 1, 5, 'TN01AB1234', '2025-07-28', '10:00', 30.00, '12:00'),
    (2, 2, 10, 'KA05CD5678', '2025-07-28', '14:30', 0.0, None), 
    (3, 3, 1, 'AP09EF9012', '2025-07-27', '09:00', 80.00, '17:00'),
    (1, 5, 12, 'TN07GH3456', '2025-07-28', '18:00', 0.0, None), 
    (5, 4, 7, 'KL08IJ7890', '2025-07-26', '11:00', 90.00, '15:30')
]
for i in reservations:
    c.execute("INSERT INTO reservation (user_id, lot_id, spot_id, vehicle_no, date_of_parking, time_of_parking, parking_cost, time_of_release) values (?, ?, ?, ?, ?, ?, ?, ?)",i)

conn.commit()
conn.close()
