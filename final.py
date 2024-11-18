import cv2
from ultralytics import YOLO
import pyttsx3 as textspeech
import json

engine = textspeech.init()

# Load the YOLO model for object detection
object_detection_model = YOLO("C:/Users/Microsoft/Documents/BE project/runs/detect/train/weights/best.pt")

# Maintain a dictionary to track quantities of detected products
product_quantities = {}

# List to store detected products in the current frame
detected_products_in_frame = []

# Text file to store billing results
text_file_name = 'billing_results.txt'

def mark_billing(product_name):
    global text_file_name

    # Check if the product is already in the current frame
    if product_name in detected_products_in_frame:
        return

    # Update product quantity in the dictionary
    if product_name in product_quantities:
        product_quantities[product_name] += 1
    else:
        product_quantities[product_name] = 1

    # Add the product to the list of detected products in the current frame
    detected_products_in_frame.append(product_name)

    # Write the billing information to the text file in JSON format
    with open(text_file_name, 'w') as file:
        json.dump(product_quantities, file)

    # Speak a statement about adding the product to the cart
    statement = f"{product_name} added to the cart"
    engine.say(statement)
    engine.runAndWait()

def detect_objects_and_billing(frame, confidence_threshold=0.7):
    global detected_products_in_frame
    results = object_detection_model(frame)[0]

    # Clear the list of detected products in the current frame
    detected_products_in_frame = []

    for result in results.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = result
        confidence = score * 100  # Convert score to percentage

        if confidence >= confidence_threshold:
            product_name = object_detection_model.names[int(class_id)]
            mark_billing(product_name)

            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.putText(frame, f'{product_name} {confidence:.2f}%', (int(x1) + 2, int(y2) - 6), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 255), 2)

            detected_products_in_frame.append(product_name)

    return frame


def display_billing_info():
    # Read the billing information from the text file and display it
    try:
        with open(text_file_name, 'r') as file:
            billing_info = json.load(file)
            print("Billing Information:")
            for product, quantity in billing_info.items():
                print(f'{product}: {quantity}')
    except FileNotFoundError:
        print("No billing information found.")

def process_video():
    vid = cv2.VideoCapture(0)

    while True:
        success, frame = vid.read()
        if not success:
            break

        frame_objects = detect_objects_and_billing(frame.copy())

        cv2.imshow('Object Detection and Billing', frame_objects)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    vid.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Clear the text file before starting the process
    open(text_file_name, 'w').close()
    
    process_video()
    display_billing_info()
