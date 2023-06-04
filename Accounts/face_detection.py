# Import necessary libraries
import cv2
import numpy as np
import base64
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

haarcascade = os.path.join(base_dir,'haarcascade_frontalface_default.xml')

# Step 1: Face Registration (Backend)
def get_face_template(face_image):
    # Read the image data from the InMemoryUploadedFile object
    face_array = np.frombuffer(face_image.read(), np.uint8)

    # Decode the numpy array to an image
    frame = cv2.imdecode(face_array, cv2.IMREAD_COLOR)

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Load the Haar cascade XML file for face detection
    face_cascade = cv2.CascadeClassifier(haarcascade)

    # Perform face detection using the Haar cascade classifier
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) > 0:
        # Extract the face region from the first detected face
        (x, y, w, h) = faces[0]
        face = gray[y:y+h, x:x+w]

        # Resize the face region to a fixed size
        face_resized = cv2.resize(face, (96, 96))

        # Calculate the Local Binary Patterns (LBP) histogram
        face_hist = cv2.calcHist([face_resized], [0], None, [256], [0, 256])
        face_hist = cv2.normalize(face_hist, face_hist).flatten()

        # Save the face template to the database
        face_template = face_hist.tobytes()        
        # Return the generated face template
        return face_template


    # If no face is detected, return None
    return None

# Step 2: Face Login (Backend)
def match_face_template(face_image,stored_template):
    # Convert the base64 encoded face image received from the frontend to a numpy array
    face_array = np.frombuffer(face_image.read(), np.uint8)

    # Decode the numpy array to an image
    frame = cv2.imdecode(face_array, cv2.IMREAD_COLOR)

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Load the Haar cascade XML file for face detection
    face_cascade = cv2.CascadeClassifier(haarcascade)

    # Perform face detection using the Haar cascade classifier
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) > 0:
        # Extract the face region from the first detected face
        (x, y, w, h) = faces[0]
        face = gray[y:y+h, x:x+w]

        # Resize the face region to a fixed size
        face_resized = cv2.resize(face, (96, 96))

        # Calculate the Local Binary Patterns (LBP) histogram
        face_hist = cv2.calcHist([face_resized], [0], None, [256], [0, 256])
        face_hist = cv2.normalize(face_hist, face_hist).flatten()

        # Save the face template to the database
        face_template = face_hist        

        stored_template = np.frombuffer(stored_template, np.float32)
        similarity = np.dot(np.array(face_template.flatten()), np.array(stored_template.flatten()))

        return similarity>=0.7

    return None

