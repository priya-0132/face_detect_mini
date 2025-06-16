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
