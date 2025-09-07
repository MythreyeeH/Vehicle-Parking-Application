from flask import Flask, render_template, request, redirect, session
import os
import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime, timedelta
import math

def init_app_routes(app):
    # Home/Login 
    @app.route('/')
    def index():
        return render_template('login.html')

    @app.route('/login', methods=['POST'])
    def login():
        role = request.form.get('role')
        email = request.form.get('email')
        password = request.form.get('password')

        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        if role == 'admin':
            c.execute("SELECT * FROM admin WHERE email = ? AND password = ?", (email, password))
            admin = c.fetchone()
            conn.close()
            if admin:
                session['admin'] = True
                session['admin_id'] = admin[0]  # Store admin ID from row
                return redirect('/admin_dashboard')
            else:
                return "Invalid Admin Credentials. <a href='/'>Try Again</a>"
        elif role == 'user':
            c.execute("SELECT id FROM user WHERE email = ? AND password = ?", (email, password))
            user = c.fetchone()
            conn.close()
            if user:
                session['user_id'] = user[0]
                return redirect('/user_dashboard')
            else:
                return "Invalid User Credentials. <a href='/'>Try Again</a>"

        conn.close()
        return "Invalid Role Selected."
    
    #user register
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            fullname = request.form.get('fullname')
            address = request.form.get('address')
            pincode = request.form.get('pincode')

            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("""
                INSERT INTO user (email, password, full_name, address, pincode)
                VALUES (?, ?, ?, ?, ?)
            """, (email, password, fullname, address, pincode))
            conn.commit()
            conn.close()

            return redirect('/')
        
        return render_template('Register.html')

    #admin_dashboard
    @app.route('/admin_dashboard')
    def admin_dashboard():
            conn = sqlite3.connect('database.db')
            conn.row_factory = sqlite3.Row
            c = conn.cursor()

            c.execute("SELECT * FROM parking_lot")
            lot_rows = c.fetchall()
            lots = []

            for row in lot_rows:
                lot_id = row['id']
                max_spots = row['max_spots']

                # Fetch actual spot occupancy status for this lot
                c.execute("""
                    SELECT id, is_occupied FROM parking_spot
                    WHERE lot_id = ?
                """, (lot_id,))
                spot_status_rows = c.fetchall()

                spot_status = {spot['id']: spot['is_occupied'] for spot in spot_status_rows}
                occupied_count = sum(1 for occupied in spot_status.values() if occupied)

                lots.append({
                    'id': lot_id,
                    'prime_location_name': row['prime_location_name'],
                    'address': row['address'],
                    'pincode': row['pincode'],
                    'max_spots': max_spots,
                    'occupied_spots': occupied_count,
                    'spot_status': spot_status
                })

            conn.close()
            return render_template('admin_dashboard.html', lots=lots)


    # Admin Registered Users
    @app.route('/admin_registered_users')
    def registered_users():
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM user")
        users = c.fetchall()
        conn.close()

        return render_template('admin_registered_users.html', users=users)

    # Admin Search
    @app.route('/admin_search', methods=['GET'])
    def admin_search():
        search_by = request.args.get('search_by')
        search_query = request.args.get('search_query', '')
        lots = []

        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        if search_by == "id" and search_query.isdigit():
            c.execute("SELECT * FROM parking_lot WHERE id = ?", (search_query,))
        elif search_by == "location":
            c.execute("SELECT * FROM parking_lot WHERE prime_location_name LIKE ?", ('%' + search_query + '%',))
        else:
            c.execute("SELECT * FROM parking_lot")
        rows = c.fetchall()

        for row in rows:
            lot_id = row['id']
            c.execute('''
                SELECT COUNT(*) AS occupied_count 
                FROM parking_spot 
                WHERE lot_id = ? AND is_occupied = 1
            ''', (lot_id,))
            occupied_count = c.fetchone()['occupied_count']

            lots.append({
                'id': lot_id,
                'prime_location_name': row['prime_location_name'],
                'address': row['address'],
                'pincode': row['pincode'],
                'price_per_hour': row['price_per_hour'],
                'max_spots': row['max_spots'],
                'occupied_spots': occupied_count
            })
        conn.close()
        return render_template('admin_search.html', lots=lots, search_by=search_by, search_query=search_query)


    # User Dashboard 
    @app.route('/user_dashboard')
    def user_dashboard():
        if 'user_id' not in session:
            return redirect('/')

        user_id = session['user_id']
        search_query = request.args.get('search_query', '')
        lots = []

        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        c.execute("""
            SELECT r.id, pl.prime_location_name, r.vehicle_no, 
                r.date_of_parking, r.time_of_parking, r.time_of_release
            FROM reservation r
            JOIN parking_lot pl ON r.lot_id = pl.id
            WHERE r.user_id = ?
            ORDER BY r.id DESC
        """, (user_id,))
        history = c.fetchall()

        if search_query:
            c.execute("""
                SELECT * FROM parking_lot 
                WHERE prime_location_name LIKE ? OR pincode LIKE ?
            """, ('%' + search_query + '%', '%' + search_query + '%'))
        else:
            c.execute("SELECT * FROM parking_lot")
        rows = c.fetchall()

        for row in rows:
            lot_id = row['id']
            max_spots = row['max_spots']
            c.execute("""
                SELECT COUNT(*) FROM parking_spot
                WHERE lot_id = ? AND is_occupied = 1
            """, (lot_id,))
            occupied_count = c.fetchone()[0]
            availability = max_spots - occupied_count
            lots.append({
                'id': lot_id,
                'address': row['address'],
                'location': row['prime_location_name'],
                'pincode': row['pincode'],
                'availability': availability
            })

        conn.close()
        return render_template('user_dashboard.html', history=history, lots=lots, search_query=search_query)
    
    # Admin Summary
    @app.route('/admin_summary')
    def admin_summary():
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        c.execute("""
            SELECT parking_lot.id, parking_lot.prime_location_name, 
                SUM(reservation.parking_cost) AS total_revenue
            FROM parking_lot
            LEFT JOIN reservation ON reservation.lot_id = parking_lot.id
            GROUP BY parking_lot.id
        """)
        revenue_data = c.fetchall()
        lot_names = [row['prime_location_name'] for row in revenue_data]
        revenues = [row['total_revenue'] if row['total_revenue'] is not None else 0 for row in revenue_data]

        c.execute("""
            SELECT parking_lot.id, parking_lot.prime_location_name,
                COUNT(parking_spot.id) AS occupied_count
            FROM parking_lot
            LEFT JOIN parking_spot 
                ON parking_spot.lot_id = parking_lot.id AND parking_spot.is_occupied = 1
            GROUP BY parking_lot.id
        """)
        occupancy_data = c.fetchall()
        lot_names2 = [row['prime_location_name'] for row in occupancy_data]
        occupied_counts = [row['occupied_count'] for row in occupancy_data]
        conn.close()

        revenue_path = os.path.join('static', 'revenue_chart.png')
        plt.figure(figsize=(5, 4))
        plt.bar(lot_names, revenues, color='skyblue')
        plt.title('Total Revenue per Parking Lot')
        plt.ylabel('Revenue (₹)')
        plt.xticks(rotation=30)
        plt.tight_layout()
        plt.savefig(revenue_path)
        plt.close()

        occupancy_path = os.path.join('static', 'occupancy_chart.png')
        plt.figure(figsize=(5, 4))
        plt.bar(lot_names2, occupied_counts, color='lightgreen')
        plt.title('Occupied Spots per Parking Lot')
        plt.ylabel('Spots')
        plt.xticks(rotation=30)
        plt.tight_layout()
        plt.savefig(occupancy_path)
        plt.close()

        return render_template('admin_summary.html',
                            revenue_chart='/static/revenue_chart.png',
                            occupancy_chart='/static/occupancy_chart.png')
    
    # User Summary 
    @app.route('/user_summary')
    def user_summary():
        if 'user_id' not in session:
            return redirect('/')
        user_id = session['user_id']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("""
            SELECT prime_location_name, SUM(parking_cost)
            FROM parking_lot, reservation
            WHERE user_id = ? AND
            reservation.lot_id=parking_lot.id
            GROUP BY lot_id;
        """, (user_id,))
        result = c.fetchall()
        conn.close()

        lot_names = [row[0] for row in result]
        costs = [row[1] for row in result]

        chart_path = None
        if lot_names and costs:
            plt.figure(figsize=(6, 4))
            plt.bar(lot_names, costs, color='orange')
            plt.title('Summary of Parking Costs per Lot')
            plt.ylabel('Total Cost')
            plt.xticks(rotation=30)
            plt.tight_layout()
            chart_path = os.path.join('static', 'user_summary_chart.png')
            plt.savefig(chart_path)
            plt.close()

        return render_template('user_summary.html', summary_chart=f'/static/user_summary_chart.png' if chart_path else None)
    
    # Admin Edit Profile
    @app.route('/admin_edit_profile', methods=['GET', 'POST'])
    def admin_edit_profile():
        if 'admin_id' not in session:
            return redirect('/')

        user_id = session['admin_id']
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            full_name = request.form.get('fullname')
            address = request.form.get('address')
            pincode = request.form.get('pincode')

            c.execute("""
                UPDATE admin
                SET email = ?, password = ?, full_name = ?, address = ?, pincode = ?
                WHERE id = ?
            """, (email, password, full_name, address, pincode, user_id))
            conn.commit()
            conn.close()

            session.clear()
            return redirect('/')

        c.execute("SELECT * FROM admin WHERE id = ?", (user_id,))
        user = c.fetchone()
        conn.close()
        return render_template('admin_edit_profile.html', user=user)

    # User Edit Profile 
    @app.route('/user_edit_profile', methods=['GET', 'POST'])
    def user_edit_profile():
        if 'user_id' not in session:
            return redirect('/')

        user_id = session['user_id']
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            full_name = request.form.get('fullname')
            address = request.form.get('address')
            pincode = request.form.get('pincode')

            c.execute("""
                UPDATE user
                SET email = ?, password = ?, full_name = ?, address = ?, pincode = ?
                WHERE id = ?
            """, (email, password, full_name, address, pincode, user_id))
            conn.commit()
            conn.close()

            session.clear()
            return redirect('/')

        c.execute("SELECT * FROM user WHERE id = ?", (user_id,))
        user = c.fetchone()
        conn.close()
        return render_template('user_edit_profile.html', user=user)

    # Release parking spot
    @app.route('/release_parking/<int:reservation_id>', methods=['GET', 'POST'])
    def release_parking(reservation_id):
        if 'user_id' not in session:
            return redirect('/')

        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        c.execute("""
            SELECT reservation.*, parking_spot.id AS spot_id
            FROM reservation
            JOIN parking_spot ON reservation.spot_id = parking_spot.id
            WHERE reservation.id = ?
        """, (reservation_id,))
        data = c.fetchone()

        if not data:
            conn.close()
            return "Reservation not found."

        if request.method == 'POST':
            releasing_time = request.form['releasing_time']
            total_cost = request.form['total_cost']

            spot_id = data['spot_id']
            lot_id = data['lot_id']
            c.execute("""
                UPDATE parking_spot
                SET is_occupied = 0
                WHERE id = ? AND lot_id = ?
            """, (spot_id, lot_id))

            c.execute("""
                UPDATE reservation
                SET time_of_release = ?, parking_cost = ?
                WHERE id = ?
            """, (releasing_time, total_cost, reservation_id))

            conn.commit()
            conn.close()
            return redirect('/user_dashboard')

        raw_time = data['time_of_parking']
        parking_time = datetime.strptime(raw_time, "%H:%M")

        now = datetime.now()
        parking_time = datetime.combine(now.date(), parking_time.time())

        if parking_time > now:
            parking_time -= timedelta(days=1)

        diff_seconds = (now - parking_time).total_seconds()
        hours_parked = max(1, math.ceil(diff_seconds / 3600))

        c.execute("SELECT price_per_hour FROM parking_lot WHERE id = ?", (data['lot_id'],))
        lot = c.fetchone()
        hourly_rate = lot['price_per_hour'] if lot else 50

        total_cost = hours_parked * hourly_rate
        releasing_time = now.strftime("%H:%M")
        conn.close()

        return render_template(
            'release_parking_spot.html',
            data=data,
            releasing_time=releasing_time,
            total_cost=total_cost
        )

    # Book Parking Lot
    @app.route('/book_parking/<int:lot_id>', methods=['GET', 'POST'])
    def book_parking(lot_id):
        if 'user_id' not in session:
            return redirect('/')

        user_id = session['user_id']
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        if request.method == 'POST':
            spot_id = int(request.form['spot_id'])
            vehicle_number = request.form['vehicle_number']

            now = datetime.now()
            date_of_parking = now.strftime('%Y-%m-%d')
            time_of_parking = now.strftime('%H:%M')  # ✅ CHANGED to HH:MM only

            c.execute("SELECT price_per_hour FROM parking_lot WHERE id = ?", (lot_id,))
            lot = c.fetchone()
            if not lot:
                conn.close()
                return "Invalid lot."

            c.execute("""
                INSERT INTO reservation (user_id, lot_id, spot_id, vehicle_no, date_of_parking, time_of_parking, parking_cost, time_of_release)
                VALUES (?, ?, ?, ?, ?, ?, ?, NULL)
            """, (user_id, lot_id, spot_id, vehicle_number, date_of_parking, time_of_parking, 0))

            c.execute("""
                UPDATE parking_spot
                SET is_occupied = 1
                WHERE id = ? AND lot_id = ?
            """, (spot_id, lot_id))

            conn.commit()
            conn.close()
            return redirect('/user_dashboard')

        c.execute("""
            SELECT id FROM parking_spot
            WHERE lot_id = ? AND is_occupied = 0
            ORDER BY id ASC
            LIMIT 1
        """, (lot_id,))
        spot_row = c.fetchone()

        if not spot_row:
            conn.close()
            return "No available spots in this lot."

        spot_id = spot_row['id']
        conn.close()

        return render_template('book_parking_spot.html', spot_id=spot_id, lot_id=lot_id, user_id=user_id)

    # Add Parking Lot
    @app.route('/add_parking_lot', methods=['GET', 'POST'])
    def add_parking_lot():
        if request.method == 'POST':
            prime_location_name = request.form['prime_location_name']
            address = request.form['address']
            pincode = request.form['pincode']
            price_per_hour = float(request.form['price_per_hour'])
            max_spots = int(request.form['max_spots'])

            conn = sqlite3.connect('database.db')
            c = conn.cursor()

            c.execute('''
                INSERT INTO parking_lot (prime_location_name, address, pincode, price_per_hour, max_spots)
                VALUES (?, ?, ?, ?, ?)
            ''', (prime_location_name, address, pincode, price_per_hour, max_spots))

            lot_id = c.lastrowid 

            for spot_id in range(1, max_spots + 1):
                c.execute('''
                    INSERT INTO parking_spot (id, lot_id, is_occupied)
                    VALUES (?, ?, 0)
                ''', (spot_id, lot_id))

            conn.commit()
            conn.close()

            return redirect('/admin_dashboard')  

        return render_template('add_parking_lot.html')

    # Edit Parking Lot
    @app.route('/edit_parking_lot/<int:lot_id>', methods=['GET', 'POST'])
    def edit_parking_lot(lot_id):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        if request.method == 'POST':
            prime_location_name = request.form['prime_location_name']
            address = request.form['address']
            pincode = request.form['pincode']
            price_per_hour = float(request.form['price_per_hour'])

            c.execute('''
                UPDATE parking_lot
                SET prime_location_name = ?, address = ?, pincode = ?, price_per_hour = ?
                WHERE id = ?
            ''', (prime_location_name, address, pincode, price_per_hour, lot_id))

            conn.commit()
            conn.close()
            return redirect('/admin_dashboard')

        c.execute('SELECT prime_location_name, address, pincode, price_per_hour FROM parking_lot WHERE id = ?', (lot_id,))
        lot = c.fetchone()
        conn.close()

        return render_template('edit_parking_lot.html', lot_id=lot_id, lot=lot)

    # Delete Parking Lot
    @app.route('/delete_parking_lot/<int:lot_id>', methods=['POST'])
    def delete_parking_lot(lot_id):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute('DELETE FROM reservation WHERE lot_id = ?', (lot_id,))
        c.execute('DELETE FROM parking_spot WHERE lot_id = ?', (lot_id,))
        c.execute('DELETE FROM parking_lot WHERE id = ?', (lot_id,))

        conn.commit()
        conn.close()

        return redirect('/admin_dashboard')

    @app.route("/occupied_slot_details", methods=["GET", "POST"])
    def occupied_slot_details():
            lot_id = int(request.args.get("lot_id") if request.method == "GET" else request.form.get("lot_id"))
            spot_id = int(request.args.get("spot_id") if request.method == "GET" else request.form.get("spot_id"))

            conn = sqlite3.connect("database.db")
            conn.row_factory = sqlite3.Row
            c = conn.cursor()

            # Fetch latest reservation for that lot and spot
            c.execute("""
                SELECT * FROM reservation 
                WHERE lot_id = ? AND spot_id = ? 
                ORDER BY id DESC LIMIT 1
            """, (lot_id, spot_id))
            record = c.fetchone()

            status = "A"
            user_id = vehicle_no = date_of_parking = time_of_parking = ""
            parking_cost = ""

            if record:
                status = "O"
                user_id = record["user_id"]
                vehicle_no = record["vehicle_no"]
                date_of_parking = record["date_of_parking"]
                time_of_parking = record["time_of_parking"]

                checkin_datetime = datetime.strptime(f"{date_of_parking} {time_of_parking}", "%Y-%m-%d %H:%M")
                current_datetime = datetime.now()
                
                duration = current_datetime - checkin_datetime
                duration_hours = max(1, (duration.days * 24) + (duration.seconds // 3600) + 1)

                c.execute("SELECT price_per_hour FROM parking_lot WHERE id = ?", (lot_id,))
                rate_row = c.fetchone()
                rate = rate_row["price_per_hour"] if rate_row else 0.0

                parking_cost = round(duration_hours * rate, 2)

            if request.method == "POST":
                if status == "O":
                    current_time_str = current_datetime.strftime("%H:%M")
                    c.execute("""
                        UPDATE reservation 
                        SET parking_cost = ?, time_of_release = ? 
                        WHERE lot_id = ? AND spot_id = ? AND id = ?
                    """, (parking_cost, current_time_str, lot_id, spot_id, record["id"]))
                    
                    c.execute("""
                        UPDATE parking_spot 
                        SET is_occupied = 0 
                        WHERE lot_id = ? AND id = ?
                    """, (lot_id, spot_id))

                    conn.commit()

                conn.close()
                return redirect("/admin_dashboard")

            conn.close()
            return render_template("occupied_spot_details.html",
                                lot_id=lot_id,
                                spot_id=spot_id,
                                status=status,
                                user_id=user_id,
                                vehicle_no=vehicle_no,
                                date_of_parking=date_of_parking,
                                time_of_parking=time_of_parking,
                                parking_cost=parking_cost)

    # Logout 
    @app.route('/logout')
    def logout():
        session.clear()
        return redirect('/')