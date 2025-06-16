from PyQt5 import QtWidgets, QtGui, QtCore
import mysql.connector
import os
import sys

class DeleteRecordWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Record")
        self.setGeometry(200, 200, 400, 300)
        self.setStyleSheet("background-color: #ECF0F1;")
        self.initUI()

    def initUI(self):
        layout = QtWidgets.QVBoxLayout()
        
        self.label = QtWidgets.QLabel("Enter Student Details for Deletion:")
        self.label.setFont(QtGui.QFont("Arial", 12))
        layout.addWidget(self.label)
        
        self.student_id_input1 = QtWidgets.QLineEdit()
        self.student_id_input1.setPlaceholderText("Enter Student ID")
        layout.addWidget(self.student_id_input1)
        
        self.student_id_input2 = QtWidgets.QLineEdit()
        self.student_id_input2.setPlaceholderText("Re-enter Student ID")
        layout.addWidget(self.student_id_input2)
        
        #self.student_name_input = QtWidgets.QLineEdit()
        #self.student_name_input.setPlaceholderText("Enter Student Name")
        #layout.addWidget(self.student_name_input)
        
        self.warning_label = QtWidgets.QLabel("⚠ WARNING: This action cannot be undone!")
        self.warning_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.warning_label)
        
        self.delete_btn = QtWidgets.QPushButton("Delete Record")
        self.delete_btn.setStyleSheet("background-color: #E74C3C; color: white; padding: 10px; font-size: 14px;")
        self.delete_btn.clicked.connect(self.delete_record)
        layout.addWidget(self.delete_btn)
        
        self.result_label = QtWidgets.QLabel("")
        layout.addWidget(self.result_label)
        
        self.setLayout(layout)
    
    def delete_record(self):
        student_id1 = self.student_id_input1.text()
        student_id2 = self.student_id_input2.text()
        student_name = self.student_name_input.text()
        
        if not student_id1 or not student_id2 or not student_name:
            QtWidgets.QMessageBox.warning(self, "Error", "⚠ All fields are required!")
            return
        
        if student_id1 != student_id2:
            QtWidgets.QMessageBox.warning(self, "Error", "⚠ Student IDs do not match!")
            return
        
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root",
                database="FaceRecognitionDB"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE id = %s", (student_id1,))
            student = cursor.fetchone()
            
            if student and student[1] == student_name:
                confirm = QtWidgets.QMessageBox.question(self, "Confirm Deletion", 
                    "Are you sure you want to delete this record? This action cannot be undone!", 
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
                
                if confirm == QtWidgets.QMessageBox.Yes:
                    cursor.execute("DELETE FROM users WHERE id = %s", (student_id1,))
                    conn.commit()
                    
                    image_path = f"Images/{student_id1}.jpg"
                    encoding_path = f"Encodings/{student_id1}.p"
                    
                    if os.path.exists(image_path):
                        os.remove(image_path)
                    if os.path.exists(encoding_path):
                        os.remove(encoding_path)
                    
                    QtWidgets.QMessageBox.information(self, "Success", "✅ Record Deleted Successfully!")
                else:
                    QtWidgets.QMessageBox.information(self, "Cancelled", "⚠ Deletion Cancelled.")
            else:
                QtWidgets.QMessageBox.warning(self, "Error", "⚠ Student ID or Name Incorrect!")
            
            cursor.close()
            conn.close()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"❌ Error: {str(e)}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = DeleteRecordWindow()
    window.show()
    sys.exit(app.exec_())
