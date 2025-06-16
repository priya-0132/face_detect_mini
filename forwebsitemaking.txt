view attendece.py

import mysql.connector
import sys
import tkinter as tk
from tkinter import ttk, messagebox

class ViewAttendanceApp:
    def __init__(self, root, role="user", username=None):  
        """Initialize Attendance Viewer GUI"""
        print(f"🔄 Initializing Attendance GUI... Role: {role}, Username: {username}")
        self.root = root
        self.role = role
        self.username = username

        self.root.title("View Attendance Records")
        self.root.geometry("900x500")
        self.root.configure(bg="#ECF0F1")

        title_label = tk.Label(self.root, text="Attendance Records", font=("Arial", 16, "bold"), bg="#ECF0F1")
        title_label.pack(pady=10)

        # ✅ Table to Show Records
        self.tree = ttk.Treeview(self.root, columns=("Username", "Total Attendance", "Last Attendance Time"), show='headings')
        self.tree.heading("Username", text="Username")
        self.tree.heading("Total Attendance", text="Total Attendance")
        self.tree.heading("Last Attendance Time", text="Last Attendance Time")

        self.tree.column("Username", width=200)
        self.tree.column("Total Attendance", width=150)
        self.tree.column("Last Attendance Time", width=200)

        self.tree.pack(pady=20, fill=tk.BOTH, expand=True)

        self.load_attendance()

    def load_attendance(self):
        """Load Attendance Data from Database"""
        print("🔄 Connecting to Database...")  
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root",
                database="FaceRecognitionDB"
            )
            cursor = conn.cursor()

            # ✅ Clear existing table data before inserting new data
            for row in self.tree.get_children():
                self.tree.delete(row)

            # ✅ If Admin: Show all records
            if self.role == "admin":
                print("🔹 Admin Role: Fetching All Attendance Records")
                cursor.execute("SELECT username, total_attendance, last_attendance_time FROM users")
            else:
                # ✅ If User: Show only their attendance record
                print(f"🔹 User Role: Fetching Attendance for {self.username}")
                cursor.execute("SELECT username, total_attendance, last_attendance_time FROM users WHERE username = %s", (self.username,))
            
            records = cursor.fetchall()
            print(f"✅ Retrieved {len(records)} records from database.")

            if not records:
                messagebox.showinfo("Info", "⚠ No attendance records found.")
            else:
                for record in records:
                    self.tree.insert("", tk.END, values=record)

            cursor.close()
            conn.close()
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"❌ {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting View Attendance GUI...")  

    # ✅ Ensure correct arguments are passed
    if len(sys.argv) < 3:
        print("⚠ Error: Missing required arguments (role & username).")
        sys.exit(1)

    role = sys.argv[1]
    username = sys.argv[2]

    root = tk.Tk()
    app = ViewAttendanceApp(root, role, username)
    root.mainloop()


add studentwith camera.py


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



ent otp.py 


import smtplib
import random
import time
import tkinter as tk
from threading import Thread

# ✅ Store OTPs temporarily (email -> OTP, timestamp)
otp_storage = {}

def send_otp(email):
    """✅ Send OTP to the given email and store it with a timestamp."""
    otp = str(random.randint(100000, 999999))  # Generate 6-digit OTP

    sender_email = "snscollege845401@gmail.com"  # Replace with your email
    sender_password = "pxfyilnmpoyzawzj"  # ✅ Use App Password

    subject = "Your OTP for Face Recognition System"
    message = f"Your OTP is: {otp}\n\nThis OTP is valid for 1 minute."

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, f"Subject: {subject}\n\n{message}")
        server.quit()

        # ✅ Store OTP with timestamp
        otp_storage[email] = {"otp": otp, "timestamp": time.time()}
        print(f"✅ OTP Sent to {email}")
        return otp  # ✅ Return OTP for verification
    except Exception as e:
        print(f"Email Error: {e}")
        return None

def verify_otp(email, entered_otp):
    """✅ Verify if the entered OTP is correct and not expired (valid for 1 min)."""
    if email not in otp_storage:
        return False  # No OTP sent

    otp_data = otp_storage[email]
    current_time = time.time()

    # ✅ Check if OTP is correct and within 60 seconds
    if otp_data["otp"] == entered_otp and (current_time - otp_data["timestamp"]) <= 60:
        return True  # ✅ OTP is valid
    return False  # ❌ OTP expired or incorrect

# ✅ Tkinter GUI for OTP Verification with Resend Option
class OTPVerificationApp:
    def __init__(self, root, email):
        self.root = root
        self.email = email
        self.root.title("OTP Verification")
        self.root.geometry("400x300")

        self.otp_label = tk.Label(root, text="Enter the OTP sent to your email:", font=("Arial", 12))
        self.otp_label.pack(pady=10)

        self.otp_entry = tk.Entry(root, font=("Arial", 14))
        self.otp_entry.pack(pady=10)

        self.verify_button = tk.Button(root, text="Verify OTP", font=("Arial", 12), command=self.verify_otp)
        self.verify_button.pack(pady=5)

        # ✅ Resend OTP Button (Initially Disabled)
        self.resend_button = tk.Button(root, text="Resend OTP (Wait 30s)", font=("Arial", 12), state=tk.DISABLED, command=self.resend_otp)
        self.resend_button.pack(pady=5)

        # ✅ Start Timer for Resend OTP Button
        self.start_resend_timer()

    def verify_otp(self):
        entered_otp = self.otp_entry.get()
        if verify_otp(self.email, entered_otp):
            tk.messagebox.showinfo("Success", "✅ OTP Verified Successfully!")
            self.root.destroy()  # ✅ Close OTP window after successful verification
        else:
            tk.messagebox.showerror("Error", "❌ Invalid or Expired OTP. Try Again.")

    def resend_otp(self):
        """✅ Resend OTP and reset the timer."""
        send_otp(self.email)
        self.resend_button.config(text="Resend OTP (Wait 30s)", state=tk.DISABLED)
        self.start_resend_timer()  # Restart 30s Timer

    def start_resend_timer(self):
        """✅ Enable Resend Button after 30 Seconds."""
        def enable_button():
            time.sleep(30)  # Wait for 30 seconds
            self.resend_button.config(text="Resend OTP", state=tk.NORMAL)

        # Run in a separate thread to avoid freezing UI
        Thread(target=enable_button, daemon=True).start()

# ✅ Example Usage:
if __name__ == "__main__":
    root = tk.Tk()
    email = "test@example.com"  # Replace with actual email input from user
    send_otp(email)  # ✅ Send OTP initially
    app = OTPVerificationApp(root, email)
    root.mainloop()



deleterecord.py 
import mysql.connector
import os
from tkinter import simpledialog, Tk

# ✅ Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="FaceRecognitionDB"
)
cursor = conn.cursor()

# ✅ Prompt for Student ID
root = Tk()
root.withdraw()
student_id = simpledialog.askstring("Input", "Enter Student ID to delete:", parent=root)

if student_id:
    cursor.execute("SELECT username FROM users WHERE username = %s", (student_id,))
    student = cursor.fetchone()

    if student:
        confirm = simpledialog.askstring("Confirm", "Type 'DELETE' to confirm:", parent=root)

        if confirm == "DELETE":
            # ✅ Delete from MySQL
            cursor.execute("DELETE FROM users WHERE username = %s", (student_id,))
            conn.commit()
            print("✅ Student record deleted from database!")

            # ✅ Remove Image & Encoding
            image_path = f"Images/{student_id}.jpg"
            encoding_path = f"Encodings/{student_id}.p"

            if os.path.exists(image_path):
                os.remove(image_path)
                print("✅ Image file deleted!")

            if os.path.exists(encoding_path):
                os.remove(encoding_path)
                print("✅ Encoding file deleted!")

        else:
            print("⚠ Deletion cancelled.")

    else:
        print("⚠ Student ID not found.")

cursor.close()
conn.close()




updateface.py


import cv2
import mysql.connector
import os
import pickle
import face_recognition
import sys
import tkinter as tk
from tkinter import messagebox, simpledialog

# ✅ Ensure Username is Provided
if len(sys.argv) != 2:
    root = tk.Tk()
    root.withdraw()
    username = simpledialog.askstring("Update Face", "Enter your Username:")
    if not username:
        print("⚠ Error: Username Required!")
        messagebox.showwarning("Error", "⚠ Username Required!")
        sys.exit(1)
else:
    username = sys.argv[1]

# ✅ Connect to MySQL
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="FaceRecognitionDB"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if not user:
        print("⚠ Username Not Found!")
        messagebox.showwarning("Error", "⚠ Username Not Found in Database!")
        sys.exit(1)
except Exception as e:
    print(f"❌ Database Connection Error: {str(e)}")
    messagebox.showerror("Database Error", f"❌ {str(e)}")
    sys.exit(1)

# ✅ Open Webcam to Capture New Image
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

print("📷 Press 'SPACE' to capture a new image or 'ESC' to exit.")
while True:
    success, img = cap.read()
    cv2.imshow("Update Face", img)
    key = cv2.waitKey(1)

    if key == 27:  # ESC key to exit
        cap.release()
        cv2.destroyAllWindows()
        sys.exit(0)

    elif key == 32:  # SPACE key to capture
        cap.release()
        cv2.destroyAllWindows()
        
        # ✅ Save New Image
        image_folder = "Images"
        encoding_folder = "Encodings"
        os.makedirs(image_folder, exist_ok=True)
        os.makedirs(encoding_folder, exist_ok=True)
        
        image_path = f"{image_folder}/{username}.jpg"
        cv2.imwrite(image_path, img)
        
        # ✅ Generate New Face Encoding
        img_user = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(img_user)

        if face_locations:
            encode = face_recognition.face_encodings(img_user, face_locations)[0]
            encoding_path = f"{encoding_folder}/{username}.p"
            with open(encoding_path, 'wb') as file:
                pickle.dump(encode, file)
            
            print("✅ Face Updated Successfully!")
            messagebox.showinfo("Success", "✅ Face Updated Successfully!")
        else:
            os.remove(image_path)
            print("⚠ No face detected. Please try again.")
            messagebox.showwarning("Error", "⚠ No face detected. Please try again.")
        break

cursor.close()
conn.close()




update record.py



import mysql.connector
import tkinter as tk
from tkinter import messagebox, simpledialog
import sys

def update_record():
    root = tk.Tk()
    root.withdraw()

    # ✅ Take Username from Command-Line Argument
    username = sys.argv[1] if len(sys.argv) > 1 else simpledialog.askstring("Update Record", "Enter Username to update:")

    if not username:
        messagebox.showwarning("Error", "⚠ Username is required!")
        return
    
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="FaceRecognitionDB"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT username, email, role, total_attendance FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user:
            messagebox.showwarning("Error", "⚠ Username Not Found!")
            return
    except Exception as e:
        messagebox.showerror("Error", f"Database Error: {str(e)}")
        return
    
    edit_window = tk.Toplevel()
    edit_window.title("Update User Record")
    edit_window.geometry("400x400")

    labels = ["Username", "Email", "Role", "Total Attendance"]
    entries = {}
    original_values = list(user)  # Store original values for reset

    for idx, label in enumerate(labels):
        tk.Label(edit_window, text=label).grid(row=idx, column=0, padx=10, pady=5)
        entry = tk.Entry(edit_window)
        entry.insert(0, user[idx] if user[idx] is not None else "")  # ✅ Handle NULL values
        entry.grid(row=idx, column=1, padx=10, pady=5)
        entries[label] = entry

    # ✅ Prevent username editing (must remain unique)
    entries["Username"].config(state="disabled")

    # ✅ Prevent role editing if user is not admin
    if user[3] == "user":
        entries["Role"].config(state="disabled")

    def save_changes():
        updated_values = [entries[label].get() for label in labels[1:]]  # Exclude username
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root",
                database="FaceRecognitionDB"
            )
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET  email=%s, role=%s, total_attendance=%s WHERE username=%s
            """, updated_values + [username])  # ✅ Don't update `username`
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Success", "✅ User record updated successfully!")
            edit_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Database Error: {str(e)}")

    def reset_fields():
        for idx, label in enumerate(labels[1:]):  # Exclude username
            entries[label].delete(0, tk.END)
            entries[label].insert(0, original_values[idx + 1] if original_values[idx + 1] is not None else "")

    save_button = tk.Button(edit_window, text="Save Changes", command=save_changes)
    save_button.grid(row=len(labels), column=0, pady=10)

    reset_button = tk.Button(edit_window, text="Reset", command=reset_fields)
    reset_button.grid(row=len(labels), column=1, pady=10)

    edit_window.mainloop()

if __name__ == "__main__":
    update_record()





usermanagement.py


import os
import sys
import mysql.connector
import tkinter as tk
from tkinter import messagebox, simpledialog
import subprocess
import cv2
import face_recognition
import pickle
import numpy as np
from send_otp import send_otp  # ✅ OTP Module
import dlib


# ✅ Database Connection Helper
def get_db_connection():
    """Returns a MySQL connection."""
    return mysql.connector.connect(host="localhost", user="root", password="root", database="FaceRecognitionDB")

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

    def login(self):
        """✅ Login using username & password"""
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()

        if not username or not password:
            messagebox.showwarning("⚠ Error", "Username and password are required!")
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT username, role FROM users WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user:
                username, role = user
                self.root.destroy()
                subprocess.Popen(["python", "G:/attendence/GUI.py", role, username])
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

        known_encodings, student_usernames = [], []
        for filename in os.listdir(encoding_folder):
            if filename.endswith(".p"):
                username = filename.split(".")[0]
                with open(os.path.join(encoding_folder, filename), 'rb') as file:
                    known_encodings.append(pickle.load(file))
                student_usernames.append(username)

        cap = cv2.VideoCapture(0)
        cap.set(3, 640)
        cap.set(4, 480)
        matched_username = None

        while True:
            success, img = cap.read()
            if not success:
                messagebox.showerror("❌ Error", "Failed to access the camera!")
                break

            imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

            faces = face_recognition.face_locations(imgS)
            encodes = face_recognition.face_encodings(imgS, faces)

            for encodeFace in encodes:
                matches = face_recognition.compare_faces(known_encodings, encodeFace)
                faceDis = face_recognition.face_distance(known_encodings, encodeFace)
                matchIndex = np.argmin(faceDis) if len(faceDis) > 0 else None

                if matchIndex is not None and matches[matchIndex]:
                    matched_username = student_usernames[matchIndex]
                    break

            cv2.imshow("Face Login", img)
            if matched_username or (cv2.waitKey(1) & 0xFF == ord('q')):
                break

        cap.release()
        cv2.destroyAllWindows()

        if matched_username:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT role FROM users WHERE username = %s", (matched_username,))
                user_role = cursor.fetchone()
                cursor.close()
                conn.close()

                if user_role:
                    role = user_role[0]
                    self.root.destroy()
                    subprocess.Popen(["python", "G:/attendence/GUI.py", role, matched_username])
                else:
                    messagebox.showerror("❌ Error", "User role not found!")
            except Exception as e:
                messagebox.showerror("❌ Error", f"Database Error: {str(e)}")
        else:
            messagebox.showerror("❌ Error", "Face Not Recognized!")

    def create_user(self):
        """✅ Create a new user with OTP verification"""
        new_username = simpledialog.askstring("Create User", "Enter New Username:")
        new_password = simpledialog.askstring("Create User", "Enter New Password:")
        email = simpledialog.askstring("Create User", "Enter Email:")

        if not new_username or not new_password or not email:
            messagebox.showwarning("⚠ Error", "All fields are required!")
            return

        sent_otp = send_otp(email)
        entered_otp = simpledialog.askstring("OTP Verification", "Enter the OTP sent to your email:")
        if entered_otp != sent_otp:
            messagebox.showerror("❌ Error", "Invalid OTP!")
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, 'user')", 
                           (new_username, new_password, email))
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("✅ Success", "User Created Successfully!")
        except mysql.connector.Error as err:
            messagebox.showerror("❌ Error", f"Database Error: {str(err)}")

    def reset_password(self):
        """✅ Reset Password using OTP"""
        username = simpledialog.askstring("Reset Password", "Enter Your Username:")
        if not username:
            messagebox.showwarning("⚠ Error", "Username is required!")
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT email FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if not user:
                messagebox.showwarning("⚠ Error", "Username Not Found!")
                return

            email = user[0]
            sent_otp = send_otp(email)
            entered_otp = simpledialog.askstring("OTP Verification", "Enter the OTP sent to your email:")
            if entered_otp != sent_otp:
                messagebox.showerror("❌ Error", "Invalid OTP!")
                return

            new_password = simpledialog.askstring("Reset Password", "Enter New Password:")
            if not new_password:
                messagebox.showwarning("⚠ Error", "New password is required!")
                return

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password = %s WHERE username = %s", (new_password, username))
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("✅ Success", "Password Reset Successfully!")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Database Error: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = UserManagementApp(root)
    root.mainloop()






encoding.py 




import cv2
import face_recognition
import pickle
import os
import mysql.connector

# ✅ Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="FaceRecognitionDB"
)
cursor = conn.cursor()

# ✅ Load student images
folderPath = 'Images'
if not os.path.exists(folderPath):
    raise FileNotFoundError(f"Error: Folder '{folderPath}' not found!")

pathList = os.listdir(folderPath)
print("Images Found:", pathList)

imgList = []
studentIds = []

for path in pathList:
    img = cv2.imread(os.path.join(folderPath, path))
    if img is not None:
        imgList.append(img)
        studentIds.append(os.path.splitext(path)[0])

print("✅ Images Loaded:", studentIds)

# ✅ Function to find encodings
def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)
        if encode:
            encodeList.append(encode[0])
    return encodeList

# ✅ Generate face encodings
print("Encoding Started ...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds]
print("Encoding Complete")

# ✅ Save encodings to file
with open("EncodeFile.p", 'wb') as file:
    pickle.dump(encodeListKnownWithIds, file)

print("✅ Encoding file 'EncodeFile.p' saved successfully!")

cursor.close()
conn.close()




gui.py


from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import os
import subprocess

class AttendanceApp(QtWidgets.QMainWindow):
    def __init__(self, user_role="user", username=""):
        super().__init__()
        self.user_role = user_role
        self.username = username
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Face Recognition Attendance System")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #2C3E50;")  # ✅ Dark Background

        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)
        layout.setAlignment(QtCore.Qt.AlignCenter)

        # ✅ Title Label (White Color)
        self.label = QtWidgets.QLabel(f"Welcome, {self.username}!", self)
        self.label.setFont(QtGui.QFont("Arial", 20, QtGui.QFont.Bold))
        self.label.setStyleSheet("color: #ECF0F1;")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.label)

        # ✅ Button Styling
        button_style = """
            QPushButton {
                background-color: #3498DB;
                color: white;
                border-radius: 10px;
                font-size: 18px;
                font-weight: bold;
                padding: 15px;
                min-width: 300px;
                transition: 0.3s;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """

        logout_button_style = """
            QPushButton {
                background-color: #E74C3C; /* ✅ Red Logout Button */
                color: white;
                border-radius: 10px;
                font-size: 18px;
                font-weight: bold;
                padding: 15px;
                min-width: 300px;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
        """

        # ✅ Define Buttons
        self.buttons = [
            ("✅ Mark Attendance", f"G:/attendence/mark_attendence.py {self.username}"),
            ("📊 View Attendance List", f"G:/attendence/view_attendence_gui.py {self.user_role} {self.username}"),  # ✅ Pass Role & Username
        ]

        if self.user_role == "admin":
            self.buttons += [
                ("➕ Add Student", "G:/attendence/add_student_with_camera.py"),
                ("✏️ Update Record", "G:/attendence/update_record.py"),
                ("📷 Update Face", "G:/attendence/update_face.py"),
                ("🗑 Delete Record", "G:/attendence/delete_record.py"),
            ]

        self.buttons.append(("🚪 Logout", "exit"))  # ✅ Logout Button

        # ✅ Create Buttons
        for text, command in self.buttons:
            btn = QtWidgets.QPushButton(text, self)

            # ✅ Apply logout style only for "Logout" button
            if text == "🚪 Logout":
                btn.setStyleSheet(logout_button_style)
            else:
                btn.setStyleSheet(button_style)

            # ✅ Check if icon exists before setting it
            icon_path = f"icons/{text.lower().replace(' ', '_')}.png"
            if os.path.exists(icon_path):
                btn.setIcon(QtGui.QIcon(icon_path))  # ✅ Add icons if available

            if command == "exit":
                btn.clicked.connect(self.close)
            else:
                btn.clicked.connect(lambda checked, cmd=command: self.run_script(cmd))

            layout.addWidget(btn)

    def run_script(self, command):
        """✅ Ensure external scripts execute correctly"""
        try:
            script_path = command.split()[0]
            args = command.split()[1:]
            print(f"🚀 Running: {script_path} with args {args}")  # Debugging log
            subprocess.Popen([sys.executable, script_path] + args, shell=True)
        except Exception as e:
            print(f"❌ Error executing {command}: {e}")

if __name__ == "__main__":
    # ✅ Ensure Role & Username are passed correctly
    if len(sys.argv) < 3:
        print("⚠ Error: Missing required arguments (role & username).")
        sys.exit(1)

    role = sys.argv[1]
    username = sys.argv[2]

    print(f"🔍 Role: {role}, Username: {username}")  # Debugging log

    app = QtWidgets.QApplication(sys.argv)
    window = AttendanceApp(user_role=role, username=username)
    window.show()
    sys.exit(app.exec_())




login.py 



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
                subprocess.Popen(["python", "G:/attendence/GUI.py", role, username])  # ✅ Direct redirection
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
                        subprocess.Popen(["python", "G:/attendence/GUI.py", role, username])  # ✅ Redirect with role
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





mark attendece.py




import mysql.connector
import cv2
import face_recognition
import pickle
import numpy as np
import sys
import os
import tkinter as tk
from tkinter import messagebox
import subprocess
from datetime import datetime
import smtplib

# ✅ Ensure username is provided
if len(sys.argv) < 2:
    print("⚠ Error: Username not provided.")
    sys.exit(1)

username = sys.argv[1]

# ✅ Email Sending Function
# ✅ Email Sending Function (Updated)
def send_attendance_email(email, username, timestamp):
    sender_email = "snscollege845401@gmail.com"  # Replace with your email
    sender_password = "pxfyilnmpoyzawzj"  # Use App Password (not regular password)

    subject = "Attendance Confirmation" 
    message = f"""
Dear {username},

Your attendance has been successfully marked on 
Date & Time: {timestamp}

To check your total attendece login at www.anukalpthakur.world



Thank you,
"Thakur and company"

for unsubscribe , mail us to "{sender_email}" with "{email}"
    """

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)

        # ✅ Encode email body in UTF-8 (Fixes ASCII issue)
        email_message = f"Subject: {subject}\n\n{message}".encode("utf-8")

        server.sendmail(sender_email, email, email_message)
        server.quit()
        print(f"📧 Email sent to {email}")
    except Exception as e:
        print(f"⚠ Email Error: {e}")

# ✅ Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="FaceRecognitionDB"
)
cursor = conn.cursor()

# ✅ Load All Stored Face Encodings
encoding_folder = "Encodings"
if not os.path.exists(encoding_folder):
    os.makedirs(encoding_folder)

encodeListKnown = []
usernames = []

print("🔄 Loading All Stored Encodings ...")
for filename in os.listdir(encoding_folder):
    if filename.endswith(".p"):
        stored_username = filename.split(".")[0]  # Extract username from filename
        with open(os.path.join(encoding_folder, filename), 'rb') as file:
            encode = pickle.load(file)
        encodeListKnown.append(encode)
        usernames.append(stored_username)

print(f"✅ Loaded {len(encodeListKnown)} Encoded Faces")

# ✅ Open Webcam
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

face_detected = False
attendance_marked = False
start_time = datetime.now()

while True:
    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    elapsed_time = (datetime.now() - start_time).total_seconds()
    if elapsed_time > 10:  # ✅ Close if no face detected for 10 seconds
        print("⏳ No Face Detected! Closing Camera...")
        break

    if faceCurFrame:
        face_detected = True

        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            matchIndex = np.argmin(faceDis) if faceDis.size > 0 else None

            if matchIndex is not None and matches[matchIndex]:
                detected_username = usernames[matchIndex]

                # ✅ Check if Detected Face Matches Logged-in User
                if detected_username != username:
                    print("❌ Face Mismatch! Redirecting to Login Page...")
                    cap.release()
                    cv2.destroyAllWindows()
                    subprocess.Popen(["python", "G:/attendence/user_management.py"])
                    sys.exit(0)

                # ✅ Fetch User Info from MySQL
                cursor.execute("SELECT email, total_attendance FROM users WHERE username = %s", (username,))
                userInfo = cursor.fetchone()

                if userInfo:
                    email, total_attendance = userInfo
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    # ✅ Mark Attendance in MySQL
                    cursor.execute("""
                        UPDATE users 
                        SET total_attendance = total_attendance + 1, last_attendance_time = %s 
                        WHERE username = %s
                    """, (timestamp, username))
                    conn.commit()

                    # ✅ Send Email Notification
                    send_attendance_email(email, username, timestamp)

                    # ✅ Draw Green Circle & Show Name & ID
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
                    radius = (x2 - x1) // 2

                    cv2.circle(img, (center_x, center_y), radius, (0, 255, 0), 4)
                    cv2.putText(img, f"Username: {username}", (x1, y1 - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    cv2.putText(img, "Attendance Marked!", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

                    cv2.imshow("Face Attendance", img)
                    cv2.waitKey(2000)  # ✅ Show for 2 seconds before closing
                    attendance_marked = True
                    break
            else:
                print("❌ Face Not Recognized!")

    cv2.imshow("Face Attendance", img)

    if attendance_marked or (cv2.waitKey(1) & 0xFF == ord('q')):
        break

# ✅ If No Known Face Found, Ask to Add New Student
if not attendance_marked:
    root = tk.Tk()
    root.withdraw()
    result = messagebox.askyesno("No Record Found", "No matching user found. Do you want to register?")
    if result:
        subprocess.Popen(["python", "G:/attendence/add_student_with_camera.py"])

cap.release()
cv2.destroyAllWindows()
cursor.close()
conn.close()






