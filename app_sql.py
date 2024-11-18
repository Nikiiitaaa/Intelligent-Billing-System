from flask import Flask, render_template, request, jsonify, g
import sqlite3

app = Flask(__name__)
DATABASE = 'trail.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# Create tables if they don't exist
def create_tables():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            customer_phone_no INTEGER PRIMARY KEY,
            customer_name TEXT NOT NULL,
            email TEXT NOT NULL
        )
    ''')
        db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Define the backend functions
def customer_exists(phn_no):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT customer_name FROM customers WHERE customer_phone_no = ?', (phn_no,))
        return cursor.fetchone() is not None

def create_customer(phn_no, name, email):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO customers (customer_phone_no, customer_name, email)
            VALUES (?, ?, ?)
        ''', (phn_no, name, email))
        db.commit()
        return cursor.lastrowid 

# Define the routes
@app.route('/')
def index():
    create_tables()  # Create tables when the app starts
    return render_template('sql.html')

@app.route('/process_customer', methods=['POST'])
def process_customer():
    phn_no = request.form['phone_number']
    
    if customer_exists(phn_no):
        return jsonify({'phone_exists': True})
    else:
        return jsonify({'phone_exists': False})

@app.route('/submit_customer_info', methods=['POST'])
def submit_customer_info():
    phn_no = request.form['phone_number']
    name = request.form['name']
    email = request.form['email']
    
    create_customer(phn_no, name, email)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)
