import sys
import os
import webbrowser
from PyQt5 import QtWidgets, QtGui, QtCore
import mysql.connector
import smtplib


def send_leave_status_email(username, status, leave_type, start_date, end_date, reject_reason, reviewed_by):
    try:
        conn = mysql.connector.connect(
            host="localhost", user="root", password="root", database="facerecognitiondb"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        conn.close()

        if not result:
            print(f"❌ Email not found for user: {username}")
            return

        email = result[0]
        subject = "Leave Status Notification"
        body = f"""Dear {username},

Your leave request has been {status.lower()}.

Leave Details:
Type         : {leave_type}
From         : {start_date}
To           : {end_date}
Reviewed by  : {reviewed_by}
"""

        if status == "Rejected" and reject_reason:
            body += f"Rejection Reason: {reject_reason}\n"

        body += "\nRegards,\nAdmin Team\nReshmi & company\nVisit: www.anukalpthakurcompany.com"

        message = f"Subject: {subject}\n\n{body}"
        sender_email = "snscollege845401@gmail.com"
        sender_password = "pxfyilnmpoyzawzj"

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, message)
        server.quit()
        print(f"✅ Email sent to {email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")


class LeaveApproval(QtWidgets.QWidget):
    def __init__(self, role, admin_name):
        super().__init__()
        self.role = role
        self.admin_name = admin_name
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Admin Leave Approval Panel")
        self.setGeometry(300, 100, 900, 600)
        self.setStyleSheet("background-color: #1E272E; color: white;")

        layout = QtWidgets.QVBoxLayout(self)

        title = QtWidgets.QLabel("🗂 Leave Requests Panel")
        title.setFont(QtGui.QFont("Segoe UI", 20, QtGui.QFont.Bold))
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("color: #00CED1; margin-bottom: 20px;")
        layout.addWidget(title)

        self.leave_table = QtWidgets.QTableWidget(self)
        self.leave_table.setColumnCount(8)
        self.leave_table.setHorizontalHeaderLabels(
            ["ID", "Username", "Type", "Start", "End", "Reason", "Status", "Doc Path"]
        )
        self.leave_table.setStyleSheet(
            "QTableWidget { background-color: #2F3640; } QHeaderView::section { background-color: #3B3B98; }"
        )
        self.leave_table.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
        self.leave_table.setColumnHidden(0, True)  # Hide ID
        self.leave_table.setColumnHidden(7, True)  # Hide Document Path
        layout.addWidget(self.leave_table)

        btn_layout = QtWidgets.QHBoxLayout()

        self.view_doc_btn = QtWidgets.QPushButton("📄 View Document")
        self.view_doc_btn.setStyleSheet(
            "background-color: #2980B9; padding: 10px; font-weight: bold; border-radius: 8px;"
        )
        self.view_doc_btn.clicked.connect(self.view_document)

        approve_btn = QtWidgets.QPushButton("✅ Approve")
        approve_btn.setStyleSheet(
            "background-color: #27AE60; padding: 10px; font-weight: bold; border-radius: 8px;"
        )
        approve_btn.clicked.connect(self.approve_leave)

        reject_btn = QtWidgets.QPushButton("❌ Reject")
        reject_btn.setStyleSheet(
            "background-color: #C0392B; padding: 10px; font-weight: bold; border-radius: 8px;"
        )
        reject_btn.clicked.connect(self.reject_leave)

        btn_layout.addWidget(self.view_doc_btn)
        btn_layout.addWidget(approve_btn)
        btn_layout.addWidget(reject_btn)

        layout.addLayout(btn_layout)

        self.load_pending_requests()

    def load_pending_requests(self):
        try:
            conn = mysql.connector.connect(
                host="localhost", user="root", password="root", database="facerecognitiondb"
            )
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, leave_type, start_date, end_date, reason, status, document_path "
                "FROM leave_requests WHERE status='Pending'"
            )
            data = cursor.fetchall()
            self.leave_table.setRowCount(len(data))
            for row_idx, row_data in enumerate(data):
                for col_idx, col_val in enumerate(row_data):
                    self.leave_table.setItem(row_idx, col_idx, QtWidgets.QTableWidgetItem(str(col_val)))
            cursor.close()
            conn.close()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error loading leave requests:\n{e}")

    def get_selected_row_data(self):
        row = self.leave_table.currentRow()
        if row == -1:
            QtWidgets.QMessageBox.warning(self, "Select a row", "Please select a leave request first.")
            return None
        return {
            "id": self.leave_table.item(row, 0).text(),
            "username": self.leave_table.item(row, 1).text(),
            "type": self.leave_table.item(row, 2).text(),
            "start": self.leave_table.item(row, 3).text(),
            "end": self.leave_table.item(row, 4).text(),
            "reason": self.leave_table.item(row, 5).text(),
            "doc": self.leave_table.item(row, 7).text(),
        }

    def approve_leave(self):
        data = self.get_selected_row_data()
        if not data:
            return

        start_date, ok1 = QtWidgets.QInputDialog.getText(
            self, "Start Date", "Start Date (YYYY-MM-DD):", text=data["start"]
        )
        if not ok1:
            return
        end_date, ok2 = QtWidgets.QInputDialog.getText(
            self, "End Date", "End Date (YYYY-MM-DD):", text=data["end"]
        )
        if not ok2:
            return

        try:
            conn = mysql.connector.connect(
                host="localhost", user="root", password="root", database="facerecognitiondb"
            )
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE leave_requests SET status='Approved', start_date=%s, end_date=%s, approved_by=%s WHERE id=%s",
                (start_date, end_date, self.admin_name, data["id"]),
            )
            conn.commit()
            cursor.close()
            conn.close()

            send_leave_status_email(
                data["username"], "Approved", data["type"], start_date, end_date, None, self.admin_name
            )
            QtWidgets.QMessageBox.information(self, "Success", "Leave approved.")
            self.load_pending_requests()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Approval failed:\n{e}")

    def reject_leave(self):
        data = self.get_selected_row_data()
        if not data:
            return

        reason, ok = QtWidgets.QInputDialog.getText(self, "Reject Reason", "Reason for rejection:")
        if not ok or not reason.strip():
            QtWidgets.QMessageBox.warning(self, "Missing", "Rejection reason is required.")
            return

        try:
            conn = mysql.connector.connect(
                host="localhost", user="root", password="root", database="facerecognitiondb"
            )
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE leave_requests SET status='Rejected', approved_by=%s, reject_reason=%s WHERE id=%s",
                (self.admin_name, reason, data["id"]),
            )
            conn.commit()
            cursor.close()
            conn.close()

            send_leave_status_email(
                data["username"], "Rejected", data["type"], data["start"], data["end"], reason, self.admin_name
            )
            QtWidgets.QMessageBox.information(self, "Success", "Leave rejected.")
            self.load_pending_requests()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Rejection failed:\n{e}")

    def view_document(self):
        data = self.get_selected_row_data()
        if not data:
            return
        if not data["doc"] or not os.path.exists(data["doc"]):
            QtWidgets.QMessageBox.warning(self, "No Document", "No valid document available for this leave.")
            return
        webbrowser.open(data["doc"])
        print("okkkk")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python approve_leave.py <admin_name> <role>")
        sys.exit(1)

    admin_name = sys.argv[1]
    role = sys.argv[2]

    if role.lower() != "admin":
        print("Access Denied. Only admins can approve/reject leave requests.")
        sys.exit(1)

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    window = LeaveApproval(role, admin_name)
    window.show()
    sys.exit(app.exec_())
