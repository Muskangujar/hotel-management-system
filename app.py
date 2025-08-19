from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
import os
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Needed for flash messages

# Database connection function
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "$Muskan12"),
            database=os.getenv("DB_NAME", "hotel_db"),
            port=int(os.getenv("DB_PORT", 3306))
        )
        return conn
    except Error as e:
        flash(f"Database connection error: {str(e)}", 'danger')
        return None
    
# --- Routes ---

# Home Page
@app.route("/")
def home():
    return render_template("index.html")

# Customers Management
@app.route("/customers")
def customers():
    conn = get_db_connection()
    if not conn:
        return redirect(url_for('home'))
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Customers ORDER BY last_name, first_name")
    customers = cursor.fetchall()
    conn.close()
    return render_template("customers.html", customers=customers)


@app.route("/add_customer", methods=["POST"])
def add_customer():
    try:
        # Get form data
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()

        # Validate required fields
        if not first_name or not last_name:
            flash("First name and last name are required", 'danger')
            return redirect(url_for('customers'))

        # Connect to database
        conn = get_db_connection()
        if not conn:
            flash("Database connection failed", 'danger')
            return redirect(url_for('customers'))

        cursor = conn.cursor()
        
        # Check if customer already exists
        cursor.execute("SELECT * FROM Customers WHERE first_name = %s AND last_name = %s", 
                       (first_name, last_name))
        if cursor.fetchone():
            flash("Customer already exists", 'warning')
            return redirect(url_for('customers'))

        # Insert new customer
        cursor.execute(
            "INSERT INTO Customers (first_name, last_name, email, phone) VALUES (%s, %s, %s, %s)",
            (first_name, last_name, email, phone)
        )
        conn.commit()
        flash("Customer added successfully", 'success')
        
    except Error as e:
        flash(f"Database error: {str(e)}", 'danger')
    except Exception as e:
        flash(f"Unexpected error: {str(e)}", 'danger')
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()
    
    return redirect(url_for('customers'))


@app.route("/delete_customer/<int:customer_id>")
def delete_customer(customer_id):
    try:
        conn = get_db_connection()
        if not conn:
            return redirect(url_for('home'))
            
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Bookings WHERE customer_id = %s", (customer_id,))
        if cursor.fetchone()[0] > 0:
            flash("Cannot delete customer with existing bookings", 'danger')
            return redirect(url_for('customers'))
            
        cursor.execute("DELETE FROM Customers WHERE customer_id = %s", (customer_id,))
        conn.commit()
        flash("Customer deleted successfully", 'success')
    except Error as e:
        flash(f"Error deleting customer: {str(e)}", 'danger')
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()
    return redirect(url_for('customers'))

# Rooms Management
@app.route("/rooms")
def rooms():
    conn = get_db_connection()
    if not conn:
        return redirect(url_for('home'))
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Rooms ORDER BY room_number")
    rooms = cursor.fetchall()
    conn.close()
    return render_template("rooms.html", rooms=rooms)

@app.route("/add_room", methods=["POST"])
def add_room():
    try:
        room_number = request.form.get("room_number", "").strip()
        room_type = request.form.get("room_type", "").strip()
        price = request.form.get("price", "0").strip()

        if not (room_number and room_type):
            flash("Room number and type are required", 'warning')
            return redirect(url_for('rooms'))

        try:
            price = float(price)
            if price <= 0:
                raise ValueError("Price must be positive")
        except ValueError:
            flash("Invalid price value", 'danger')
            return redirect(url_for('rooms'))

        conn = get_db_connection()
        if not conn:
            return redirect(url_for('home'))
            
        cursor = conn.cursor()
        cursor.execute("SELECT room_id FROM Rooms WHERE room_number = %s", (room_number,))
        if cursor.fetchone():
            flash("Room number already exists", 'danger')
            return redirect(url_for('rooms'))

        cursor.execute(
            "INSERT INTO Rooms (room_number, room_type, price) VALUES (%s, %s, %s)",
            (room_number, room_type, price)
        )
        conn.commit()
        flash("Room added successfully", 'success')
    except Error as e:
        flash(f"Error adding room: {str(e)}", 'danger')
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()
    return redirect(url_for('rooms'))

@app.route("/delete_room/<int:room_id>")
def delete_room(room_id):
    try:
        conn = get_db_connection()
        if not conn:
            return redirect(url_for('home'))
            
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Bookings WHERE room_id = %s", (room_id,))
        if cursor.fetchone()[0] > 0:
            flash("Cannot delete room with existing bookings", 'danger')
            return redirect(url_for('rooms'))
            
        cursor.execute("DELETE FROM Rooms WHERE room_id = %s", (room_id,))
        conn.commit()
        flash("Room deleted successfully", 'success')
    except Error as e:
        flash(f"Error deleting room: {str(e)}", 'danger')
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()
    return redirect(url_for('rooms'))

# Bookings Management
@app.route("/bookings")
def bookings():
    conn = get_db_connection()
    if not conn:
        return redirect(url_for('home'))
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT b.booking_id, 
               c.customer_id,
               CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
               r.room_id,
               r.room_number, 
               r.room_type,
               r.price,
               b.check_in, 
               b.check_out,
               DATEDIFF(b.check_out, b.check_in) * r.price AS total_cost
        FROM Bookings b
        JOIN Customers c ON b.customer_id = c.customer_id
        JOIN Rooms r ON b.room_id = r.room_id
        WHERE b.check_out > CURDATE()
        ORDER BY b.check_in
    """)
    bookings = cursor.fetchall()

    cursor.execute("SELECT customer_id, CONCAT(first_name, ' ', last_name) AS name FROM Customers ORDER BY last_name")
    customers = cursor.fetchall()
    
    cursor.execute("SELECT room_id, room_number, room_type, price FROM Rooms WHERE status='Available'")
    available_rooms = cursor.fetchall()

    conn.close()
    return render_template("bookings.html", 
                         bookings=bookings, 
                         customers=customers, 
                         rooms=available_rooms,
                         today=datetime.now().strftime('%Y-%m-%d'))

@app.route("/add_booking", methods=["POST"])
def add_booking():
    try:
        customer_id = request.form['customer_id']
        room_id = request.form['room_id']
        check_in = request.form['check_in']
        check_out = request.form['check_out']

        if not (customer_id and room_id and check_in and check_out):
            flash("All fields are required", 'warning')
            return redirect(url_for('bookings'))

        conn = get_db_connection()
        if not conn:
            return redirect(url_for('home'))
            
        cursor = conn.cursor()
        
        # Check if room is available for the dates
        cursor.execute("""
            SELECT COUNT(*) FROM Bookings 
            WHERE room_id = %s 
            AND (
                (check_in <= %s AND check_out >= %s) OR
                (check_in <= %s AND check_out >= %s) OR
                (check_in >= %s AND check_out <= %s)
            )
        """, (room_id, check_in, check_in, check_out, check_out, check_in, check_out))
        
        if cursor.fetchone()[0] > 0:
            flash("Room is not available for the selected dates", 'danger')
            return redirect(url_for('bookings'))
        
        # Add booking
        cursor.execute(
            "INSERT INTO Bookings (customer_id, room_id, check_in, check_out) VALUES (%s, %s, %s, %s)",
            (customer_id, room_id, check_in, check_out)
        )
        
        # Update room status
        cursor.execute("UPDATE Rooms SET status='Occupied' WHERE room_id = %s", (room_id,))
        
        conn.commit()
        flash("Booking added successfully", 'success')
    except Error as e:
        flash(f"Error adding booking: {str(e)}", 'danger')
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()
    return redirect(url_for('bookings'))

@app.route("/checkout/<int:booking_id>/<int:room_id>")
def checkout(booking_id, room_id):
    try:
        conn = get_db_connection()
        if not conn:
            return redirect(url_for('home'))
            
        cursor = conn.cursor()
        
        # Delete booking
        cursor.execute("DELETE FROM Bookings WHERE booking_id = %s", (booking_id,))
        
        # Update room status
        cursor.execute("UPDATE Rooms SET status='Available' WHERE room_id = %s", (room_id,))
        
        conn.commit()
        flash("Checkout processed successfully", 'success')
    except Error as e:
        flash(f"Error during checkout: {str(e)}", 'danger')
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()
    return redirect(url_for('bookings'))

# Run the application
if __name__ == "__main__":
    app.run(debug=True)