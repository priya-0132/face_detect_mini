import sys
from PyQt5 import QtWidgets, QtGui, QtCore
import mysql.connector
from datetime import datetime
import os
import shutil

class LeaveApplication(QtWidgets.QWidget):
    def __init__(self, username, role):
        super().__init__()
        self.username = username
        self.role = role
        self.uploaded_file_path = None
        self.initUI()

    def initUI(self):
        print(f"Username: {self.username}, Role: {self.role}")

        if self.role not in ["admin", "user"]:
            QtWidgets.QMessageBox.critical(self, "Invalid Role", "Unknown role detected. Please check your role.")
            self.close()
            return

        self.setWindowTitle("Apply for Leave")
        self.setGeometry(300, 200, 500, 600)
        self.setStyleSheet("background-color: #2C3E50; color: white;")

        layout = QtWidgets.QVBoxLayout(self)

        title = QtWidgets.QLabel("Leave Application Form")
        title.setFont(QtGui.QFont("Arial", 18, QtGui.QFont.Bold))
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("color: #ECF0F1;")
        layout.addWidget(title)

        layout.addWidget(QtWidgets.QLabel("Select Leave Type:"))
        self.leave_type = QtWidgets.QComboBox()
        self.leave_type.addItems(["Select Leave Type", "Sick Leave", "Casual Leave", "Emergency Leave", "Other"])
        self.leave_type.setStyleSheet("padding: 10px; background-color: #34495E; color: white; border-radius: 8px;")
        layout.addWidget(self.leave_type)
        self.leave_type.currentTextChanged.connect(self.toggle_upload)

        layout.addWidget(QtWidgets.QLabel("Start Date:"))
        self.start_date = QtWidgets.QDateEdit(QtCore.QDate.currentDate())
        self.start_date.setCalendarPopup(True)
        self.start_date.setStyleSheet("padding: 10px; background-color: #34495E; color: white; border-radius: 8px;")
        layout.addWidget(self.start_date)

        layout.addWidget(QtWidgets.QLabel("End Date:"))
        self.end_date = QtWidgets.QDateEdit(QtCore.QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.setStyleSheet("padding: 10px; background-color: #34495E; color: white; border-radius: 8px;")
        layout.addWidget(self.end_date)

        layout.addWidget(QtWidgets.QLabel("Reason:"))
        self.reason_input = QtWidgets.QTextEdit()
        self.reason_input.setStyleSheet("padding: 10px; background-color: #34495E; color: white; border-radius: 8px;")
        layout.addWidget(self.reason_input)

        self.upload_btn = QtWidgets.QPushButton("Upload Sick Leave Document (PDF, Max 1MB)")
        self.upload_btn.setStyleSheet("background-color: #3498DB; color: white; padding: 10px; border-radius: 8px;")
        self.upload_btn.clicked.connect(self.upload_document)
        self.upload_btn.setVisible(False)  # Hidden by default
        layout.addWidget(self.upload_btn)

        submit_btn = QtWidgets.QPushButton("Submit Leave Request")
        submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #27AE60;
            }
        """)
        submit_btn.clicked.connect(self.submit_request)
        layout.addWidget(submit_btn)

    def toggle_upload(self, text):
        self.upload_btn.setVisible(text == "Sick Leave")
        if text != "Sick Leave":
            self.uploaded_file_path = None  # Reset uploaded file if leave type changes

    def upload_document(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf)")
        if file_path:
            if os.path.getsize(file_path) > 1 * 1024 * 1024:
                QtWidgets.QMessageBox.warning(self, "File Too Large", "File size must be less than 1MB.")
                return
            upload_dir = os.path.join(os.path.expanduser("~"), "Desktop", "attendence", "leave")
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            dest_path = os.path.join(upload_dir, f"{self.username}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf")
            shutil.copyfile(file_path, dest_path)
            self.uploaded_file_path = dest_path
            QtWidgets.QMessageBox.information(self, "File Uploaded", "PDF uploaded successfully.")

    def submit_request(self):
        leave_type = self.leave_type.currentText()
        start_date = self.start_date.date()
        end_date = self.end_date.date()
        start_date_str = start_date.toString("yyyy-MM-dd")
        end_date_str = end_date.toString("yyyy-MM-dd")
        reason = self.reason_input.toPlainText()

        if leave_type == "Select Leave Type":
            QtWidgets.QMessageBox.warning(self, "Input Error", "Please select a leave type.")
            return

        if end_date < start_date:
            QtWidgets.QMessageBox.warning(self, "Input Error", "End Date cannot be earlier than Start Date.")
            return

        if not reason.strip():
            QtWidgets.QMessageBox.warning(self, "Input Error", "Please enter a valid reason.")
            return

        if len(reason) > 500:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Reason is too long. Please shorten it.")
            return

        if leave_type == "Sick Leave" and not self.uploaded_file_path:
            QtWidgets.QMessageBox.warning(self, "Missing Document", "Sick leave requires uploading a PDF document.")
            return

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root",
                database="facerecognitiondb"
            )
            cursor = conn.cursor()

            insert_query = """
                INSERT INTO leave_requests 
                (username, role, leave_type, start_date, end_date, reason, status, document_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                self.username,
                self.role,
                leave_type,
                start_date_str,
                end_date_str,
                reason,
                "Pending",
                self.uploaded_file_path if leave_type == "Sick Leave" else None
            ))
            conn.commit()
            cursor.close()
            conn.close()

            QtWidgets.QMessageBox.information(self, "Success", "Leave request submitted successfully!")
            self.close()

        except mysql.connector.Error as e:
            QtWidgets.QMessageBox.critical(self, "Database Error", f"MySQL Error: {e}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Unexpected error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python leave.py <username> <role>")
        sys.exit(1)

    username = sys.argv[1]
    role = sys.argv[2]

    print(f"Passed username: {username}, role: {role}")

    app = QtWidgets.QApplication(sys.argv)
    window = LeaveApplication(username, role)
    window.show()
    sys.exit(app.exec_())
