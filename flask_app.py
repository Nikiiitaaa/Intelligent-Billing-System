from flask import Flask, render_template, jsonify
from flask_cors import CORS
import threading
from final import process_video
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Your existing code here...

# New route to start detection
@app.route('/start_detection')
def start_detection():
    # You can start your object detection script here
    # Use threading to run it in the background
    detection_thread = threading.Thread(target=start_detection_process)
    detection_thread.start()

    return jsonify({'message': 'Object detection started'})

def start_detection_process():
    # Your object detection script goes here
    # For example, you can call your process_video function
    process_video()

if __name__ == '__main__':
    app.run(debug=True)
