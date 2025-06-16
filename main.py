import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
import mysql.connector
from datetime import datetime

# ✅ Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="FaceRecognitionDB"
)
cursor = conn.cursor()

# ✅ Load Background Image
imgBackground = cv2.imread('Resources/background.png')

# ✅ Load Mode Images
folderModePath = 'Resources/Modes'
if not os.path.exists(folderModePath):
    raise FileNotFoundError(f"Error: Folder '{folderModePath}' not found!")

modePathList = os.listdir(folderModePath)
imgModeList = [cv2.imread(os.path.join(folderModePath, path)) for path in modePathList]

# ✅ Load Face Encodings File
encode_file_path = "EncodeFile.p"

if not os.path.exists(encode_file_path):
    raise FileNotFoundError("Error: EncodeFile.p not found!")

print("Loading Encode File ...")
with open(encode_file_path, 'rb') as file:
    encodeListKnownWithIds = pickle.load(file)

encodeListKnown, studentIds = encodeListKnownWithIds
print("✅ Encode File Loaded")

# ✅ Open Webcam
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# ✅ Initialize Variables
modeType = 0
counter = 0
id = -1

while True:
    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[162:162 + 480, 55:55 + 640] = img

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                id = studentIds[matchIndex]

                # ✅ Fetch Student Info from MySQL
                cursor.execute("SELECT * FROM Students WHERE id = %s", (id,))
                studentInfo = cursor.fetchone()

                if studentInfo:
                    last_attendance_time = studentInfo[7]
                    secondsElapsed = (datetime.now() - last_attendance_time).total_seconds()

                    if secondsElapsed > 30:
                        cursor.execute("""
                            UPDATE Students 
                            SET total_attendance = total_attendance + 1, last_attendance_time = %s 
                            WHERE id = %s
                        """, (datetime.now(), id))

                        conn.commit()
                        print(f"✅ Attendance updated for {studentInfo[1]}")

    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)

cursor.close()
conn.close()
