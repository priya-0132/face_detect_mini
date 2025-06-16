import mysql.connector
import tkinter as tk
from tkinter import messagebox, simpledialog  # ✅ Fix: Added simpledialog import
import subprocess
import cv2
import face_recognition
import pickle
import os
import numpy as np
from send_otp import send_otp  # ✅ OTP Module

class UserManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("User Management")
        self.root.geometry("400x400")
        self.initUI()

    def initUI(self):
        tk.Label(self.root, text="Face Recognition System", font=("Arial", 14, "bold")).pack(pady=10)

        tk.Label(self.root, text="Username:").pack()
        self.entry_username = tk.Entry(self.root)
        self.entry_username.pack()

        tk.Label(self.root, text="Password:").pack()
        self.entry_password = tk.Entry(self.root, show="*")
        self.entry_password.pack()

        tk.Button(self.root, text="🔑 Login", command=self.login).pack(pady=5)
        tk.Button(self.root, text="📷 Login with Face", command=self.login_with_face).pack(pady=5)
        tk.Button(self.root, text="🆕 Create New User", command=self.create_user).pack(pady=5)
        tk.Button(self.root, text="🔄 Reset Password", command=self.reset_password).pack(pady=5)
        tk.Label(self.root, text="Managed & Developed by reshmi & Co.", font=("Arial", 9, "italic"), bg="#f0f0f0", fg="black").pack(pady=5)
        tk.Label(self.root, text="📧 Email: reshmi@gehu.ac.in | 📸 Insta: Reshmi_kantura", font=("Arial", 9, "italic"), bg="#f0f0f0", fg="black").pack()

    def login(self):
        """✅ Login using username & password"""
        username = self.entry_username.get()
        password = self.entry_password.get()

        if not username or not password:
            messagebox.showwarning("⚠ Error", "Username and password are required!")
            return

        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root", database="FaceRecognitionDB")
            cursor = conn.cursor()
            cursor.execute("SELECT username, role FROM users WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user:
                role = user[1]
                self.root.destroy()  # ✅ Close the login window immediately
                subprocess.Popen(["python", "F:/attendence/GUI.py", role, username])  # ✅ Direct redirection
            else:
                messagebox.showerror("❌ Error", "Invalid Username or Password!")
        except Exception as e:
            messagebox.showerror("❌ Database Error", f"{str(e)}")

    def login_with_face(self):
        """✅ Login using Face Recognition"""
        encoding_folder = "Encodings"
        if not os.path.exists(encoding_folder):
            messagebox.showerror("Error", "No stored face encodings found!")
            return

        encodeListKnown = []
        stored_usernames = []

        for filename in os.listdir(encoding_folder):
            if filename.endswith(".p"):
                username = filename.split(".")[0]
                with open(os.path.join(encoding_folder, filename), 'rb') as file:
                    encode = pickle.load(file)
                encodeListKnown.append(encode)
                stored_usernames.append(username)

        cap = cv2.VideoCapture(0)
        cap.set(3, 640)
        cap.set(4, 480)

        messagebox.showinfo("📷 Face Recognition", "Align your face with the camera.")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for encoding in face_encodings:
                matches = face_recognition.compare_faces(encodeListKnown, encoding, tolerance=0.5)
                if True in matches:
                    matched_idx = matches.index(True)
                    username = stored_usernames[matched_idx]
                    
                    # ✅ Fetch User Role from MySQL
                    conn = mysql.connector.connect(host="localhost", user="root", password="root", database="FaceRecognitionDB")
                    cursor = conn.cursor()
                    cursor.execute("SELECT role FROM users WHERE username = %s", (username,))
                    user = cursor.fetchone()
                    cursor.close()
                    conn.close()
                    
                    if user:
                        role = user[0]
                        cap.release()
                        cv2.destroyAllWindows()
                        self.root.destroy()
                        subprocess.Popen(["python", "F:/attendence/GUI.py", role, username])  # ✅ Redirect with role
                        return

            cv2.imshow("Face Login", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        messagebox.showerror("❌ Error", "Face Not Recognized!")

    def create_user(self):
        """✅ Create a new user with OTP verification and Face Capture"""
        new_username = simpledialog.askstring("Create User", "Enter New Username:")
        new_password = simpledialog.askstring("Create User", "Enter New Password:")
        email = simpledialog.askstring("Create User", "Enter Email:")

        if not new_username or not new_password or not email:
            return  

        sent_otp = send_otp(email)
        entered_otp = simpledialog.askstring("OTP Verification", "Enter the OTP sent to your email:")
        if entered_otp != sent_otp:
            return  
        encoding_folder = "Encodings"
        os.makedirs(encoding_folder, exist_ok=True)

        encodeListKnown = []
        stored_usernames = []

        for filename in os.listdir(encoding_folder):
            if filename.endswith(".p"):
                stored_username = filename.split(".")[0]
                with open(os.path.join(encoding_folder, filename), 'rb') as file:
                    encode = pickle.load(file)
                encodeListKnown.append(encode)
                stored_usernames.append(stored_username)

        cap = cv2.VideoCapture(0)
        cap.set(3, 640)
        cap.set(4, 480)

        messagebox.showinfo("📷 Face Capture", "Align your face with the camera.")

        while True:
            ret, frame = cap.read()
            cv2.imshow("Register Face", frame)
            key = cv2.waitKey(1)

            if key == 32:  
                cap.release()
                cv2.destroyAllWindows()

                image_folder = "Images"
                os.makedirs(image_folder, exist_ok=True)
                image_path = f"{image_folder}/{new_username}.jpg"
                cv2.imwrite(image_path, frame)

                img_new = face_recognition.load_image_file(image_path)
                face_locations = face_recognition.face_locations(img_new)

                if not face_locations:
                    os.remove(image_path)
                    messagebox.showwarning("⚠ Error", "No face detected. Try again!")
                    return

                new_encoding = face_recognition.face_encodings(img_new, face_locations)[0]

                for idx, stored_encoding in enumerate(encodeListKnown):
                    match = face_recognition.compare_faces([stored_encoding], new_encoding, tolerance=0.5)
                    if match[0]:
                        os.remove(image_path)  
                        messagebox.showinfo("⚠ Duplicate Face", f"This face is already registered with {stored_usernames[idx]}.")
                        return

                encoding_path = f"{encoding_folder}/{new_username}.p"
                with open(encoding_path, 'wb') as file:
                    pickle.dump(new_encoding, file)

                try:
                    conn = mysql.connector.connect(host="localhost", user="root", password="root", database="FaceRecognitionDB")
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, 'user')", 
                                (new_username, new_password, email))
                    conn.commit()
                    cursor.close()
                    conn.close()
                except mysql.connector.Error as err:
                    messagebox.showerror("❌ Error", f"Database Error: {str(err)}")
                return
