from flask import Flask
import subprocess
import sys
import os

app = Flask(__name__)

@app.route('/')
def home():
    # ✅ Run GUI.py when accessed via Localhost
    python_executable = sys.executable  # Get current Python executable
    gui_path = os.path.join("G:/attendence", "GUI.py")  # Path to GUI.py

    # ✅ Start GUI.py in a new process (non-blocking)
    subprocess.Popen([python_executable, gui_path], shell=True)

    return "✅ GUI is Opening... Check Your Desktop!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # ✅ Accessible on Local Network
