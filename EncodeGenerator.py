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
