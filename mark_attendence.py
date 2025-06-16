import cv2
import face_recognition
import pickle
import sys
import os
import mysql.connector
import dlib
from datetime import datetime
from scipy.spatial import distance as dist
import smtplib

def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

def send_attendance_email(email, username, timestamp):
    sender_email = "snscollege845401@gmail.com"
    sender_password = "pxfyilnmpoyzawzj"
    subject = "Attendance Confirmation"
    message = f"""
Dear {username},

Your attendance has been successfully marked on 
Date & Time: {timestamp}

To check your total attendance, login at www.reshmi.geu.ac.in

Thank you,
"Thakur and company"

For unsubscribe, mail us at "{sender_email}" with "{email}"
    """
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        email_message = f"Subject: {subject}\n\n{message}"
        server.sendmail(sender_email, email, email_message.encode("utf-8"))
        server.quit()
        print(f"📧 Email sent to {email}")
    except Exception as e:
        print(f"⚠ Email Error: {e}")

if len(sys.argv) < 2:
    print("⚠ Error: Username not provided.")
    sys.exit(1)

username = sys.argv[1]

db = mysql.connector.connect(host="localhost", user="root", password="root", database="FaceRecognitionDB")
cursor = db.cursor()

target_encoding_file = f"Encodings/{username}.p"
if not os.path.exists(target_encoding_file):
    print("❌ No encoding found for user. Exiting...")
    sys.exit(1)

with open(target_encoding_file, 'rb') as file:
    known_encoding = pickle.load(file)

cap = cv2.VideoCapture(0)
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

EYE_AR_THRESH = 0.20
EYE_AR_CONSEC_FRAMES = 2
blink_counter = 0
blink_detected = False
attendance_marked = False

while True:
    success, img = cap.read()
    if not success:
        print("❌ Camera Error! Exiting...")
        break

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    for face in faces:
        x, y, w, h = face.left(), face.top(), face.width(), face.height()
        # Face encoding expects (top, right, bottom, left)
        face_enc = face_recognition.face_encodings(img, [(y, x + w, y + h, x)])

        if face_enc and face_recognition.compare_faces([known_encoding], face_enc[0])[0]:
            cv2.circle(img, (x + w // 2, y + h // 2), max(w, h) // 2, (0, 255, 0), 2)
            landmarks = predictor(gray, face)
            left_eye = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)]
            right_eye = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)]
            left_ear = eye_aspect_ratio(left_eye)
            right_ear = eye_aspect_ratio(right_eye)
            ear = (left_ear + right_ear) / 2.0
            
            for (ex, ey) in left_eye + right_eye:
                cv2.circle(img, (ex, ey), 2, (255, 0, 0), -1)

            if ear < EYE_AR_THRESH:
                blink_counter += 1
            else:
                if blink_counter >= EYE_AR_CONSEC_FRAMES:
                    print("✅ Eye Blink Detected!")
                    blink_detected = True
                blink_counter = 0

            if blink_detected and not attendance_marked:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("SELECT email FROM users WHERE username = %s", (username,))
                result = cursor.fetchone()
                if result:
                    email = result[0]
                    cursor.execute("""
                        UPDATE users SET total_attendance = total_attendance + 1, last_attendance_time = %s
                        WHERE username = %s
                    """, (timestamp, username))
                    db.commit()
                    send_attendance_email(email, username, timestamp)
                    print("✅ Attendance Marked!")
                    attendance_marked = True
                    cv2.putText(img, "Attendance Marked!", (x, y + h + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                else:
                    print(f"❌ Email not found for username: {username}")

    cv2.imshow("Face Recognition Attendance", img)
    if attendance_marked:
        cv2.waitKey(2000)
        break
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
cursor.close()
db.close()
