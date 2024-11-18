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
        FOREIGN KEY (customer_id) REFERENCES customers(customer_name),
        FOREIGN KEY (product_id) REFERENCES products(product_Name)
    )
''')
        
    conn.commit()
    

def create_customer(name, email):
    cursor.execute('''
        INSERT INTO customers (name, email)
        VALUES (?, ?)
    ''', (name, email))
    conn.commit()
    return cursor.lastrowid 

def insert_products():
    products_data=[
        (1, 'Colgate', 50),
        (2, 'Kitkat', 10),
        (3, 'Lays-Chips', 10),
        (4, 'Maggi', 15),
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
        cursor.execute('SELECT price FROM products WHERE product_Name = ?', (product_Name,))
        price = cursor.fetchone()[0]
        total_price = price * quantity

        cursor.execute('''
            INSERT INTO orders (customer_name, Name, quantity, total_price, order_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (customer_name, product_Name, quantity, total_price, order_date))

    conn.commit()
customer_name = input("Enter customer name: ")
customer_email = input("Enter customer email: ")

# Create the customer
customer_id = create_customer(customer_name, customer_email)

# Get user input for orders
products_and_quantities = {}

while True:
    try:
        product_Name = input("Enter the product Name (0 to finish): ")
        quantity = int(input("Enter the quantity: "))
        products_and_quantities[product_Name] = quantity
    except ValueError:
        print("Invalid input. Please enter a valid number.")

# Create the order with user input
create_order(customer_name, products_and_quantities)

# Display orders
cursor.execute('''
    SELECT customers.customer_name, products.product_Name, quantity, total_price, order_date
    FROM orders
    JOIN customers ON orders.customer_name = customers.customer_name
    JOIN products ON orders.product_Name = products.product_Name
''')

orders = cursor.fetchall()
final_price = 0
printed_customer_name = False

print("\nAll Orders:")
for order in orders:
    if not printed_customer_name:
        print(f'Customer: {order[0]}')
        printed_customer_name = True

    print(f'Product: {order[1]}, Quantity: {order[2]}, Total Price: ${order[3]}, Date: {order[4]}')
    final_price += order[3]

print(f'\nFinal Price: ${final_price:.2f}')

# Delete the orders table
cursor.execute('DROP TABLE IF EXISTS orders')


# Close the connection
conn.close()