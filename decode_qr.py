import cv2

filename = "qr.png"

image = cv2.imread(filename)

#initialize the cv2 qrcode detector 
dectector = cv2.QRCodeDetector()

#detect and decode

data, vertices_array, binary_qrcode = dectector.detectAndDecode(image)

if vertices_array is not None: 
    print("qr code data:" , data)

else: 
    print("error")