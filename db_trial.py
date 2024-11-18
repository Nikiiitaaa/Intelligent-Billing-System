import json
import sqlite3
from datetime import datetime

conn = sqlite3.connect("data.db")
cursor = conn.cursor()

def create_tables():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY,
        customer_name TEXT NOT NULL,
        email TEXT NOT NULL
    )
''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        Product_Id INTEGER PRIMARY KEY,
        product_Name TEXT NOT NULL,
        Price REAL NOT NULL
    )
''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY,
        customer_name TEXT,
        product_Name TEXT,
        quantity INTEGER NOT NULL,
        total_price REAL NOT NULL,
        order_date TEXT NOT NULL,
        FOREIGN KEY (customer_name) REFERENCES customers(customer_name),
        FOREIGN KEY (product_Name) REFERENCES products(product_Name)
    )
''')
        
    conn.commit()

def create_customer(name, email):
    cursor.execute('''
        INSERT INTO customers (customer_name, email)
        VALUES (?, ?)
    ''', (name, email))
    conn.commit()
    return cursor.lastrowid 

def insert_products():
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
    cursor.executemany('INSERT OR IGNORE INTO products(Product_Id, product_Name, Price) VALUES (?, ?, ?)', products_data)
    conn.commit()
def create_order(customer_name, products_and_quantities):
    order_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for product_Name, quantity in products_and_quantities.items():
        cursor.execute('SELECT Price FROM products WHERE product_Name = ?', (product_Name,))
        result = cursor.fetchone()

        # Check if the result is not None before accessing its elements
        if result is not None:
            price = result[0]
            total_price = price * quantity

            cursor.execute('''
                INSERT INTO orders (customer_name, product_Name, quantity, total_price, order_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (customer_name, product_Name, quantity, total_price, order_date))
        else:
            print(f"Product {product_Name} not found in the products table.")

    conn.commit()



def customer_exists(name):
    cursor.execute('SELECT customer_id FROM customers WHERE customer_name = ?', (name,))
    return cursor.fetchone() is not None
def take_user_input():
    customer_name = input("Enter customer name: ")

    # Check if the customer already exists
    if not customer_exists(customer_name):
        customer_email = input("Enter customer email: ")
        create_customer(customer_name, customer_email)

    # Read the input data from the file
    try:
        with open('billing_results.txt', 'r') as file:
            products_and_quantities = json.load(file)
    except FileNotFoundError:
        print("File 'billing_results.txt' not found.")
        return

    # Create the order with the loaded dictionary
    create_order(customer_name, products_and_quantities)

def update_order():
    
    while True:
        order_id = int(input("Enter the order ID to update/delete/add (0 to finish): "))

        if order_id == 0:
            break

        # Check if the order exists
        cursor.execute('SELECT * FROM orders WHERE order_id = ?', (order_id,))
        order = cursor.fetchone()

        if order:
            print("Existing Order Details:")
            print(f'Order ID: {order[0]}, Customer: {order[1]}, Product: {order[2]}, Quantity: {order[3]}, Total Price: Rs.{order[4]}, Date: {order[5]}')

            action = input("Choose action (update/delete/add): ").lower()

            if action == 'update':
                new_quantity = int(input("Enter the new quantity: "))
                cursor.execute('SELECT Price FROM products WHERE product_Name = ?', (order[2],))
                price = cursor.fetchone()[0]
                new_total_price = price * new_quantity

                cursor.execute('''
                    UPDATE orders
                    SET quantity = ?, total_price = ?
                    WHERE order_id = ?
                ''', (new_quantity, new_total_price, order_id))
                conn.commit()

                print(f"Order {order_id} updated successfully.")

            elif action == 'delete':
                cursor.execute('DELETE FROM orders WHERE order_id = ?', (order_id,))
                conn.commit()
                print(f"Order {order_id} deleted successfully.")

            elif action == 'add':
                new_product_Name = input("Enter the new product Name: ")
                new_quantity = int(input("Enter the quantity: "))
                cursor.execute('SELECT Price FROM products WHERE product_Name = ?', (new_product_Name,))
                price = cursor.fetchone()[0]
                new_total_price = price * new_quantity

                cursor.execute('''
                    INSERT INTO orders (customer_name, product_Name, quantity, total_price, order_date)
                    VALUES (?, ?, ?, ?, ?)
                ''', (order[1], new_product_Name, new_quantity, new_total_price, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                conn.commit()

                print(f"New product added to order {order_id} successfully.")

            else:
                print("Invalid action. Please choose 'update', 'delete', or 'add'.")
        else:
            print(f"Order {order_id} not found.")

def display_orders():
    cursor.execute('''
        SELECT order_id, customers.customer_name, products.product_Name, quantity, total_price, order_date
        FROM orders
        JOIN customers ON orders.customer_name = customers.customer_name
        JOIN products ON orders.product_Name = products.product_Name
    ''')

    orders = cursor.fetchall()
    final_price = 0

    print("\nAll Orders:")
    for order in orders:
        print(f'Order ID: {order[0]}, Customer: {order[1]}, Product: {order[2]}, Quantity: {order[3]}, Total Price: Rs.{order[4]}, Date: {order[5]}')
        final_price += order[4]

    print(f'\nFinal Price: Rs.{final_price:.2f}')
    
    

# Call the functions


create_tables()
insert_products()
take_user_input()
display_orders()

ans = input("Do you want to Update Bill(yes/No) ").lower()
if(ans == 'yes'):
    try:
        update_order()
    except ValueError:
        print("Invalid input. Please enter a valid number.")
    display_orders()
    cursor.execute('DROP TABLE IF EXISTS orders')
    conn.commit()
else:
    print("Thank you for shopping")
    cursor.execute('DROP TABLE IF EXISTS orders')
    conn.commit()

# Close the connection
conn.close()
