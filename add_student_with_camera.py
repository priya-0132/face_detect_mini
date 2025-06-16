import cv2
import mysql.connector
import os
import pickle
import face_recognition
from tkinter import simpledialog, Tk, messagebox

# ✅ Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="FaceRecognitionDB"
)
cursor = conn.cursor()

# ✅ Create Necessary Folders
image_folder = "Images"
encoding_folder = "Encodings"
os.makedirs(image_folder, exist_ok=True)
os.makedirs(encoding_folder, exist_ok=True)

# ✅ Open Webcam to Capture Image
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

print("📷 Press 'SPACE' to capture an image or 'ESC' to exit.")

while True:
    success, img = cap.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(100, 100))

    # ✅ Draw Rectangles Around Detected Faces
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow("Capture Image", img)

    key = cv2.waitKey(1)

    if key == 27:  # ESC key to exit
        print("❌ Exiting without adding student.")
        cap.release()
        cv2.destroyAllWindows()
        exit()
    
    elif key == 32 and len(faces) > 0:  # SPACE key to capture only if a face is detected
        cap.release()
        cv2.destroyAllWindows()

        # ✅ Prompt User for Student Details (Using Tkinter)
        root = Tk()
        root.withdraw()

        student_id = simpledialog.askstring("Input", "Enter Student ID:", parent=root)
        student_name = simpledialog.askstring("Input", "Enter Student Name:", parent=root)
        email = simpledialog.askstring("Input", "Enter Email:", parent=root)

        if not (student_id and student_name and email):
            messagebox.showerror("Error", "⚠ All fields are required!")
            cap = cv2.VideoCapture(0)  # Reopen webcam for another attempt
            continue  # Restart loop to capture again

        # ✅ Save Image
        image_path = f"{image_folder}/{student_id}.jpg"
        cv2.imwrite(image_path, img)
        print(f"✅ Image Saved as {image_path}")

        # ✅ Verify Face Detection Before Encoding
        img_student = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(img_student)

        if not face_locations:
            messagebox.showerror("Error", "⚠ No face detected in the captured image. Please try again.")
            os.remove(image_path)  # Remove the invalid image
            cap = cv2.VideoCapture(0)  # Reopen webcam
            continue  # Restart loop to capture again

        # ✅ Generate Face Encoding
        encode = face_recognition.face_encodings(img_student, face_locations)[0]

        # ✅ Save Encoding to File
        encoding_path = f"{encoding_folder}/{student_id}.p"
        with open(encoding_path, 'wb') as file:
            pickle.dump(encode, file)
        print(f"✅ Face Encoding Saved as {encoding_path}")

        # ✅ Check if Student Already Exists in `users` Table
        cursor.execute("SELECT username FROM users WHERE username = %s", (student_id,))
        existing_student = cursor.fetchone()

        if existing_student:
            print(f"📝 Student {student_id} already exists. Image and encoding updated.")
        else:
            # ✅ Insert New Student Data into `users` Table
            cursor.execute("""
                INSERT INTO users (username, password, email, role, total_attendance, last_attendance_time)
                VALUES (%s, %s, %s, 'user', %s, NULL)
            """, (student_id, student_id, email, 0))
            conn.commit()
            print("✅ New Student Data Saved Successfully!")

        break

cap.release()
cv2.destroyAllWindows()
cursor.close()
conn.close()
