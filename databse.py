import mysql.connector

# ✅ Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",   # Change if different
    password="root",  # Change if different
    database="FaceRecognitionDB"
)
cursor = conn.cursor()

# ✅ Sample student data
data = [
    ("101", "Anukalp Thakur", "Computer Science", 2023, 0, "A", 1, None),
    ("102", "John Doe", "Mechanical Engineering", 2022, 0, "B", 2, None),
    ("103", "Alice Smith", "Electronics", 2021, 0, "C", 3, None)
]

# ✅ Insert data into MySQL
cursor.executemany("""
    INSERT INTO Students (id, name, major, starting_year, total_attendance, standing, year, last_attendance_time)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
""", data)

conn.commit()
print("✅ Student data added successfully!")

cursor.close()
conn.close()
