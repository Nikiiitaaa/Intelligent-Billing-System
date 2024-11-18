from flask import Flask, render_template, request, flash, redirect, url_for, session , get_flashed_messages,jsonify
import sqlite3
import threading
import subprocess
from datetime import datetime
import json
import pyqrcode
import time


app = Flask(__name__)
app.secret_key = "123"
app.config["DEBUG"] = True
app.config['TESTING'] = True

con = sqlite3.connect("database.db")
con.execute("create table if not exists customer(pid integer primary key,name text,address text,contact integer,mail text)")
con.close()

def get_connection():
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    return conn, cur

def create_tables():
    conn, cur = get_connection()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        customer_name TEXT NOT NULL,
        customer_phone_no INTEGER PRIMARY KEY
        
    )
''')
    
    cur.execute('''
    CREATE TABLE IF NOT EXISTS products (
        Product_Id INTEGER PRIMARY KEY,
        product_Name TEXT NOT NULL,
        Price REAL NOT NULL
    )
''')
    
    cur.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY,
        product_Name TEXT,
        quantity INTEGER NOT NULL,
        total_price REAL NOT NULL,
        order_date TEXT NOT NULL,
        FOREIGN KEY (product_Name) REFERENCES products(product_Name)
    )
''')
        
    conn.commit()

running_process = None
def run_script():
    global running_process
    running_process = subprocess.Popen(["python", "final_cam.py"])



# Function to stop the running Python script
def stop_script():
    global running_process
    if running_process:
        running_process.terminate()
def insert_products():
    conn, cur = get_connection()
    products_data=[
        (1, 'Colgate', 50),
        (2, 'Kitkat', 10),
        (3, 'Lays-Chips', 10),
        (4, 'Maggie', 15),
        (5, 'Parle-G', 10),
        (6, 'Ponds', 45),
        (7, 'Rin-Soap', 10),
        (8, 'Sprite', 20)
    ]
    cur.executemany('INSERT OR IGNORE INTO products(Product_Id, product_Name, Price) VALUES (?, ?, ?)', products_data)
    conn.commit()
    
    cur.execute('SELECT product_Name FROM products')
    product_names = [row[0] for row in cur.fetchall()]  # Extracting product names from the fetched rows
    conn.close()

    return product_names

@app.route('/get_product_names')
def get_product_names():
    product_names = insert_products()
    return jsonify(product_names)
def showBillPopup():
    return redirect(url_for('save_customer'))
def create_order( products_and_quantities):
    conn, cur = get_connection()
    order_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for product_Name, quantity in products_and_quantities.items():
        cur.execute('SELECT Price FROM products WHERE product_Name = ?', (product_Name,))
        result = cur.fetchone()

        # Check if the result is not None before accessing its elements
        if result is not None:
            price = result[0]
            total_price = price * quantity

            cur.execute('''
                INSERT INTO orders ( product_Name, quantity, total_price, order_date)
                VALUES ( ?, ?, ?, ?)
            ''', ( product_Name, quantity, total_price, order_date))
        else:
            print(f"Product {product_Name} not found in the products table.")

    conn.commit()
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        con = sqlite3.connect("database.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("select * from customer where name=? and mail=?", (name, password))
        data = cur.fetchone()

        if data:
            session["name"] = data["name"]
            session["mail"] = data["mail"]
            return redirect(url_for("h14"))  # Redirect to h14.html
        else:
            flash("Username and Password Mismatch", "danger")
    return redirect(url_for("index"))

@app.route('/h14')
def h14():
    return render_template("h14.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            name = request.form['name']
            address = request.form['address']
            contact = request.form['contact']
            mail = request.form['mail']
            con = sqlite3.connect("database.db")
            cur = con.cursor()
            cur.execute("insert into customer(name,address,contact,mail)values(?,?,?,?)",(name, address, contact, mail))
            con.commit()
            flash("Record Added Successfully", "success")
        except:
            flash("Error in Insert Operation", "danger")
        finally:
            return redirect(url_for("index"))
            con.close()

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return render_template('index.html')

@app.route('/about.html')
def about():
    return render_template("about.html")

@app.route('/team.html')
def team():
    return render_template("team.html")

@app.route('/feedback.html')
def feedback():
    return render_template("feedback.html")

@app.route('/start_billing', methods=['GET'])
def start_billing():
    # Start the billing process in a separate thread
    threading.Thread(target=run_script).start()
    return 'Billing process started', 200

# Route to stop the billing process
@app.route('/stop_billing', methods=['GET'])
def stop_billing():
    # Stop the running script
    stop_script()
    return 'Billing process stopped', 200

@app.route('/orders')
def orders():
    conn, cur = get_connection()

    # Check if the 'orders' table exists in the database
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='orders'")
    orders_table_exists = cur.fetchone()

    # If the 'orders' table does not exist, or if it's empty, check if the billing results file exists
    if not orders_table_exists:
        try:
            with open('billing_results.txt', 'r') as file:
                products_and_quantities = json.load(file)
        except FileNotFoundError:
            print("File 'billing_results.txt' not found.")
            return render_template('orders.html', orders=[], final_price=0)

        create_order(products_and_quantities)
    else:
        # Check if the 'orders' table is empty
        cur.execute("SELECT COUNT(*) FROM orders")
        orders_count = cur.fetchone()[0]

        if orders_count == 0:
            try:
                with open('billing_results.txt', 'r') as file:
                    products_and_quantities = json.load(file)
            except FileNotFoundError:
                print("File 'billing_results.txt' not found.")
                return render_template('orders.html', orders=[], final_price=0)

            create_order(products_and_quantities)

    # Fetch orders from the database
    cur.execute("SELECT * FROM orders")
    orders = cur.fetchall()

    # Calculate total price
    final_price = sum(order[3] for order in orders)

    conn.close()
    return render_template('orders.html', orders=orders, final_price=final_price)

# Route to handle editing orders
@app.route('/edit_order', methods=['POST'])
def edit_order():
    order_id = request.form['order_id']
    quantity = int(request.form['quantity'])

    conn, cur = get_connection()

    # Fetch product name and unit price from the orders table
    cur.execute("SELECT product_Name, total_price FROM orders WHERE order_id = ?", (order_id,))
    result = cur.fetchone()
    
    if result:
        product_name, total_price = result

        # Fetch unit price of the product from the products table
        cur.execute("SELECT Price FROM products WHERE product_Name = ?", (product_name,))
        unit_price = cur.fetchone()[0]

        # Calculate the new total price
        new_total_price = unit_price * quantity

        # Update the quantity and total price in the database
        cur.execute("UPDATE orders SET quantity = ?, total_price = ? WHERE order_id = ?", (quantity, new_total_price, order_id))
        conn.commit()

    conn.close()
    return redirect(url_for('orders'))


# Route to add a new product
@app.route('/add_product', methods=['POST'])
def add_product():
    product_name = request.form['product_name']
    quantity = int(request.form['quantity'])
    price = float(request.form['price'])

    conn, cur = get_connection()


    # Check if the product already exists in the orders table
    cur.execute("SELECT * FROM orders WHERE product_name = ?", (product_name,))
    existing_product = cur.fetchone()

    if existing_product:
        # If the product exists, increment the quantity
        new_quantity = existing_product[2] + quantity
        # Update the total price
        total_price = new_quantity * price
        cur.execute("UPDATE orders SET quantity = ?, total_price = ? WHERE product_name = ?", (new_quantity, total_price, product_name))
    else:
        # If the product does not exist, insert a new entry
        cur.execute("INSERT INTO orders (product_name, quantity, total_price, order_date) VALUES (?, ?, ?, CURRENT_TIMESTAMP)", (product_name, quantity, quantity * price))

    conn.commit()
    conn.close()
    return redirect(url_for('orders'))

   # Route to delete an order
@app.route('/delete_order', methods=['POST'])
def delete_order():
    order_id = request.form['order_id']

    conn, cur = get_connection()


    # Fetch the total price of the order to be deleted
    cur.execute("SELECT total_price FROM orders WHERE order_id = ?", (order_id,))
    total_price = cur.fetchone()[0]

    # Delete the order from the database
    cur.execute("DELETE FROM orders WHERE order_id = ?", (order_id,))
    conn.commit()

    # Update the total price
    cur.execute("SELECT SUM(total_price) FROM orders")
    new_total_price = cur.fetchone()[0]

    if new_total_price is None:
        new_total_price = 0

    conn.close()
    return redirect(url_for('orders'))

def get_orders_total_price():
    # Connect to the SQLite database
    conn, cur = get_connection()

    # Fetch data from the database
    cur.execute("SELECT * FROM orders")
    orders = cur.fetchall()
    final_price = 0
    for order in orders:
        final_price += order[3]

    # Close the database connection
    conn.close()

    return final_price



@app.route('/show_qr_code', methods=["GET", "POST"])
def show_qr_code():
    if request.method == "POST":
        # Fetch final price from get_orders function
        final_price = get_orders_total_price()
        gst_rate = 18  # Assuming GST rate is 18%
        total_with_gst = final_price + (final_price * (gst_rate / 100))
        # Construct UPI string with the final price
        s = f"upi://pay?pa=8600569230@axl&pn=gauri%20maid&mc=0000&mode=02&purpose=00&am={total_with_gst}"

        # Generate QR code
        url = pyqrcode.create(s)
        url.svg("static/myqr.svg", scale=8)
        url.png("static/myqr.png", scale=6)
        messages = get_flashed_messages()
        return render_template("qr_code.html", code="myqr.png", messages=messages)
    else:
        return render_template("form.html")

@app.route('/save_customer', methods=['POST'])
def save_customer():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        
        # Check if customer exists
        conn, cur = get_connection()
        cur.execute("SELECT * FROM customers WHERE customer_name = ? AND customer_phone_no = ?", (name, phone))
        existing_customer = cur.fetchone()
        if not existing_customer:
            # Insert new customer into the database
            cur.execute("INSERT INTO customers (customer_name, customer_phone_no) VALUES (?, ?)", (name, phone))
            conn.commit()
        
        # Fetch orders from the database
        cur.execute("SELECT * FROM orders")
        orders = cur.fetchall()
        
        # Fetch customer details from the database (assuming only one customer for simplicity)
        

        # Calculate total price
        total_price = sum(order[3] for order in orders)
        
        gst_rate = 18  # Assuming GST rate is 18%
        total_with_gst = total_price + (total_price * (gst_rate / 100))
        # Get current date and time
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cur.close()
        conn.close()

        return render_template('invoice.html', orders=orders, customer_name=name, customer_phone=phone, total_price=total_price,gst_rate=gst_rate, total_with_gst=total_with_gst, current_date=current_date)
    else:
        return redirect(url_for('orders'))
@app.route('/clear_orders', methods=['POST'])
def clear_orders():
    if request.method == 'POST':
        # Connect to the SQLite database
        conn, cur = get_connection()

        # Delete all records from the orders table
        cur.execute("DELETE FROM orders")

        # Commit the transaction and close the connection
        conn.commit()
        conn.close()

        # Redirect to the h14 route
        return redirect(url_for('h14'))
    else:
        # Handle other HTTP methods (not expected in this case)
        return redirect(url_for('h14'))
@app.route('/pay', methods=['POST'])
def pay():
    # Logic for payment
    return show_qr_code()

if __name__ == '__main__':
    create_tables()
    insert_products()
    app.run(debug=True)
