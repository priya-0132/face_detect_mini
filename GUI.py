from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import subprocess

class AttendanceApp(QtWidgets.QMainWindow):
    def __init__(self, user_role="user", username=""):
        super().__init__()
        self.user_role = user_role
        self.username = username
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Employee Management")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #2C3E50;")

        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)
        layout.setAlignment(QtCore.Qt.AlignCenter)

        self.label = QtWidgets.QLabel(f"Welcome, {self.username}!", self)
        self.label.setFont(QtGui.QFont("Arial", 20, QtGui.QFont.Bold))
        self.label.setStyleSheet("color: #ECF0F1;")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.label)

        # Button Styles
        button_style = """
            QPushButton {
                background-color: #3498DB;
                color: white;
                border-radius: 10px;
                font-size: 18px;
                font-weight: bold;
                padding: 15px;
                min-width: 300px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """
        logout_button_style = """
            QPushButton {
                background-color: #E74C3C;
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

        # Common Buttons for All Users
        self.buttons = [
            ("✅ Mark Attendance", f"C:/Users/laptop/OneDrive/Desktop/attendence/mark_attendence.py {self.username}"),
            ("📊 View Attendance List", f"C:/Users/laptop/OneDrive/Desktop/attendence/view_attendence_gui.py {self.user_role} {self.username}"),
            ("📝 Apply for Leave", f"C:/Users/laptop/OneDrive/Desktop/attendence/leave.py {self.username} {self.user_role}"),
            ("📂 Leave History", f"C:/Users/laptop/OneDrive/Desktop/attendence/leave_viewer.py {self.username}"),
        ]

        # Admin-Only Buttons
        if self.user_role == "admin":
            self.buttons += [
                ("✅ Approve Leave Requests", f"C:/Users/laptop/OneDrive/Desktop/attendence/approve_leave.py {self.username} {self.user_role}"),
                ("➕ Add Employee", "C:/Users/laptop/OneDrive/Desktop/attendence/add_student_with_camera.py"),
                ("✏️ Update Record", "C:/Users/laptop/OneDrive/Desktop/attendence/update_record.py"),
                ("📷 Update Face", "C:/Users/laptop/OneDrive/Desktop/attendence/update_face.py"),
                ("🗑 Delete Record", "C:/Users/laptop/OneDrive/Desktop/attendence/delete_record.py"),
            ]

        # Logout Button
        self.buttons.append(("🚪 Logout", "user_management.py"))

        # Create and Connect Buttons
        for text, command in self.buttons:
            btn = QtWidgets.QPushButton(text, self)
            btn.setStyleSheet(logout_button_style if text == "🚪 Logout" else button_style)

            # Connect click event
            if command == "exit":
                btn.clicked.connect(self.close)
            elif command == "user_management.py":
                btn.clicked.connect(self.logout_redirect)
            else:
                btn.clicked.connect(lambda checked, cmd=command: self.run_script(cmd))

            layout.addWidget(btn)

    def logout_redirect(self):
        """Redirect to user_management.py when Logout is clicked"""
        try:
            print("🚪 Logging out and redirecting to user_management.py...")
            subprocess.Popen([sys.executable, "user_management.py"], shell=True)
            self.close()
        except Exception as e:
            print(f"❌ Error redirecting to user_management.py: {e}")

    def run_script(self, command):
        """Run external scripts via subprocess"""
        try:
            script_path = command.split()[0]
            args = command.split()[1:]
            print(f"🚀 Running: {script_path} with args {args}")
            subprocess.Popen([sys.executable, script_path] + args, shell=True)
        except Exception as e:
            print(f"❌ Error executing {command}: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("⚠ Error: Missing required arguments (role & username).")
        sys.exit(1)

    role = sys.argv[1]
    username = sys.argv[2]

    print(f"🔍 Role: {role}, Username: {username}")

    app = QtWidgets.QApplication(sys.argv)
    window = AttendanceApp(user_role=role, username=username)
    window.show()
    sys.exit(app.exec_())
