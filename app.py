from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

if not app.secret_key:
    raise RuntimeError("FLASK_SECRET_KEY is missing. Add it to your .env file.")


# connecting

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "pharmacy_db")
    )


# creating database

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE,
            password VARCHAR(50),
            role VARCHAR(10)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS medicines (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            quantity INT,
            expiry_date DATE,
            price FLOAT,
            added_by VARCHAR(50)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS activity_log (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50),
            action VARCHAR(200),
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS bills (
            id INT AUTO_INCREMENT PRIMARY KEY,
            customer_name VARCHAR(100),
            total_amount FLOAT,
            bill_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_by VARCHAR(50)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS bill_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            bill_id INT NOT NULL,
            medicine_id INT NOT NULL,
            medicine_name VARCHAR(100) NOT NULL,
            quantity INT NOT NULL,
            price FLOAT NOT NULL,
            subtotal FLOAT NOT NULL,
            FOREIGN KEY (bill_id) REFERENCES bills(id) ON DELETE CASCADE,
            FOREIGN KEY (medicine_id) REFERENCES medicines(id)
        )
    """)



    # if no user entered, i am inserting default users
    cur.execute("SELECT * FROM users WHERE username='manager'")
    if not cur.fetchone():
        cur.execute("INSERT INTO users (username, password, role) VALUES ('manager', 'admin123', 'manager')")
    
    cur.execute("SELECT * FROM users WHERE username='staff'")
    if not cur.fetchone():
        cur.execute("INSERT INTO users (username, password, role) VALUES ('staff', 'staff123', 'staff')")
    
    conn.commit()
    cur.close()
    conn.close()

init_db()


# login 

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            session['user'] = user['username']
            session['role'] = user['role']
            flash(f"Welcome {user['username']}!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password!", "danger")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for('login'))


# Dashboard

@app.route('/home')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', role=session['role'])


# Adding  Medicine which is done only by staff

@app.route('/add', methods=['GET', 'POST'])
def add_medicine():
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['role'] != 'staff':
        flash("Only staff can add medicines!", "danger")
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form['name']
        quantity = int(request.form['quantity'])
        expiry_date = datetime.strptime(request.form['expiry_date'], '%Y-%m-%d').date()
        price = float(request.form['price'])

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO medicines (name, quantity, expiry_date, price, added_by)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, quantity, expiry_date, price, session['user']))
        conn.commit()

        cur.execute("INSERT INTO activity_log (username, action) VALUES (%s, %s)",
                    (session['user'], f"Added medicine {name} ({quantity} units)"))
        conn.commit()

        cur.close()
        conn.close()

        flash("Medicine added successfully!", "success")
        return redirect(url_for('view_medicines'))

    return render_template('add_medicine.html')


# to see medicines

@app.route('/medicines')
def view_medicines():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM medicines")
    medicines = cur.fetchall()
    cur.close()
    conn.close()

    today = datetime.now().date()
    soon_threshold = today + timedelta(days=10)
    expired, expiring_soon, low_stock = [], [], []

    for m in medicines:
        expiry = m['expiry_date']
        if expiry < today:
            expired.append(m['name'])
        elif today <= expiry <= soon_threshold:
            expiring_soon.append(m['name'])
        if m['quantity'] < 5:
            low_stock.append(m['name'])

    if expired:
        flash(f"Expired medicines: {', '.join(expired)}", "danger")
    if expiring_soon:
        flash(f"Medicines expiring soon (within 10 days): {', '.join(expiring_soon)}", "warning")
    if low_stock:
        flash(f"Low stock alert (less than 5 units): {', '.join(low_stock)}", "info")

    return render_template(
        'view_medicines.html',
        medicines=medicines,
        today=today,
        soon_threshold=soon_threshold,
        role=session['role']
    )


# to delete Medicine which is done only by staff

@app.route('/delete/<int:id>')
def delete_medicine(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['role'] != 'staff':
        flash("Only staff can delete medicines!", "danger")
        return redirect(url_for('view_medicines'))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM medicines WHERE id=%s", (id,))
    med = cur.fetchone()
    if med:
        cur.execute("DELETE FROM medicines WHERE id=%s", (id,))
        conn.commit()
        cur.execute("INSERT INTO activity_log (username, action) VALUES (%s, %s)",
                    (session['user'], f"Deleted medicine {med['name']}"))
        conn.commit()

    cur.close()
    conn.close()

    flash("Medicine deleted successfully!", "info")
    return redirect(url_for('view_medicines'))


# Manager screen incld activity log

@app.route('/manager_dashboard')
def manager_dashboard():
    if 'user' not in session or session['role'] != 'manager':
        flash("Access denied: Manager only.", "danger")
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM activity_log ORDER BY timestamp DESC")
    logs = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('manager_dashboard.html', logs=logs)


# summary for manager

@app.route('/manager_summary')
def manager_summary():
    if 'user' not in session or session['role'] != 'manager':
        flash("Access denied: Manager only.", "danger")
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM medicines")
    medicines = cur.fetchall()
    cur.close()
    conn.close()

    today = datetime.now().date()
    soon_threshold = today + timedelta(days=10)

    total_medicines = len(medicines)
    total_quantity = sum(m['quantity'] for m in medicines)
    total_value = sum(m['quantity'] * m['price'] for m in medicines)

    expired = [m for m in medicines if m['expiry_date'] < today]
    expiring_soon = [m for m in medicines if today <= m['expiry_date'] <= soon_threshold]

    expired_count = len(expired)
    expiring_soon_count = len(expiring_soon)
    wastage_value = sum(m['quantity'] * m['price'] for m in expired)

    return render_template(
        'manager_summary.html',
        total_medicines=total_medicines,
        total_quantity=total_quantity,
        total_value=total_value,
        expired_count=expired_count,
        expiring_soon_count=expiring_soon_count,
        wastage_value=wastage_value
    )
# billing 
@app.route('/billing', methods=['GET', 'POST'])
def billing():
    if 'user' not in session or session['role'] != 'staff':
        flash("Access denied: Staff only.", "danger")
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # Fetch medicines for dropdown/select in the form
    cur.execute("SELECT * FROM medicines")
    medicines = cur.fetchall()

    if request.method == 'POST':
        customer_name = request.form['customer_name']
        medicine_ids = request.form.getlist('medicine_id[]')
        quantities = request.form.getlist('quantity[]')

        if not medicine_ids or not quantities:
            flash("Please select at least one medicine.", "danger")
            return redirect(url_for('billing'))

        total_amount = 0
        bill_items = []
        today = datetime.now().date()
        soon_threshold = today + timedelta(days=10)

        for i in range(len(medicine_ids)):
            med_id = int(medicine_ids[i])
            qty = int(quantities[i])

            # Get medicine info
            cur.execute("SELECT * FROM medicines WHERE id=%s", (med_id,))
            med = cur.fetchone()
            if not med:
                flash(f"Medicine not found!", "danger")
                return redirect(url_for('billing'))

            # Check expiry
            if med['expiry_date'] < today:
                flash(f"Warning: {med['name']} is expired!", "danger")
            elif today <= med['expiry_date'] <= soon_threshold:
                flash(f" Alert: {med['name']} will expire soon!", "warning")


            # Check stock
            new_quantity = med['quantity'] - qty
            if new_quantity < 0:
                flash(f"Not enough stock for {med['name']}!", "danger")
                return redirect(url_for('billing'))

            # Update stock
            cur.execute("UPDATE medicines SET quantity=%s WHERE id=%s", (new_quantity, med_id))

            # Alerts
            if today <= med['expiry_date'] <= soon_threshold:
                flash(f"Alert: {med['name']} will expire soon!", "warning")
            if new_quantity < 5:
                flash(f"Alert: Low stock for {med['name']} after this sale!", "info")

            # Subtotal
            subtotal = qty * med['price']
            total_amount += subtotal

            bill_items.append({
                'medicine_id': med_id,
                'medicine_name': med['name'],
                'quantity': qty,
                'price': med['price'],
                'subtotal': subtotal
            })

        # Insert bill
        cur.execute("""
            INSERT INTO bills (customer_name, total_amount, created_by)
            VALUES (%s, %s, %s)
        """, (customer_name, total_amount, session['user']))
        conn.commit()

        bill_id = cur.lastrowid

        # Insert all bill items
        for item in bill_items:
            cur.execute("""
                INSERT INTO bill_items (bill_id, medicine_id, medicine_name, quantity, price, subtotal)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (bill_id, item['medicine_id'], item['medicine_name'], item['quantity'], item['price'], item['subtotal']))
        conn.commit()

        cur.close()
        conn.close()

        flash(f"Bill generated for {customer_name}. Total: ₹{total_amount:.2f}", "success")
        return redirect(url_for('print_bill', bill_id=bill_id))

    cur.close()
    conn.close()
    return render_template('billing.html', medicines=medicines)

@app.route('/print_bill/<int:bill_id>')
def print_bill(bill_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # Fetch bill info
    cur.execute("SELECT * FROM bills WHERE id=%s", (bill_id,))
    bill = cur.fetchone()

    if not bill:
        flash("Bill not found!", "danger")
        return redirect(url_for('billing'))

    # Fetch bill items
    cur.execute("SELECT * FROM bill_items WHERE bill_id=%s", (bill_id,))
    items = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('print_bill.html', bill=bill, items=items)


# Run

if __name__ == '__main__':
    app.run(
        host=os.getenv("FLASK_HOST", "127.0.0.1"),
        port=int(os.getenv("FLASK_PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "False").lower() == "true"
    )
