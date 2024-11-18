from flask import Flask, render_template, request
import threading
import subprocess
import psutil
import sqlite3


app = Flask(__name__)

# Global variable to store the process of the running script
running_process = None

# Function to run the Python script
def run_script():
    global running_process
    running_process = subprocess.Popen(["python", "final_cam.py"])
def print_bill():
    result = subprocess.run(["python", "db_trail.py",customer_name], capture_output=True, text=True)
    return result.stdout


# Function to stop the running Python script
def stop_script():
    global running_process
    if running_process:
        running_process.terminate()

# Route to start the billing process
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

@app.route('/print_bill', methods=['GET'])
def print_bill_page():
    return render_template('print_bill.html')

# Route to print the bill

@app.route('/print_bill', methods=['POST'])
def print_bill():
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        bill_result = print_bill(customer_name)
        return bill_result
    else:
        return render_template('print_bill.html')
# Route to render the HTML file
@app.route('/')
def index():
    return render_template('h14.html')

if __name__ == "__main__":
    app.run(debug=True)
