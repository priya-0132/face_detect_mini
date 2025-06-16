import smtplib
import random
import time
import tkinter as tk
from threading import Thread

# ✅ Store OTPs temporarily (email -> OTP, timestamp)
otp_storage = {}

def send_otp(email):
    """✅ Send OTP to the given email and store it with a timestamp."""
    otp = str(random.randint(100000, 999999))  # Generate 6-digit OTP

    sender_email = "snscollege845401@gmail.com"  # Replace with your email
    sender_password = "pxfyilnmpoyzawzj"  # ✅ Use App Password

    subject = "Your OTP for Face Recognition System"
    message = f"Your OTP is: {otp}\n\nThis OTP is valid for 1 minute."

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, f"Subject: {subject}\n\n{message}")
        server.quit()

        # ✅ Store OTP with timestamp
        otp_storage[email] = {"otp": otp, "timestamp": time.time()}
        print(f"✅ OTP Sent to {email}")
        return otp  # ✅ Return OTP for verification
    except Exception as e:
        print(f"Email Error: {e}")
        return None

def verify_otp(email, entered_otp):
    """✅ Verify if the entered OTP is correct and not expired (valid for 1 min)."""
    if email not in otp_storage:
        return False  # No OTP sent

    otp_data = otp_storage[email]
    current_time = time.time()

    # ✅ Check if OTP is correct and within 60 seconds
    if otp_data["otp"] == entered_otp and (current_time - otp_data["timestamp"]) <= 60:
        return True  # ✅ OTP is valid
    return False  # ❌ OTP expired or incorrect

# ✅ Tkinter GUI for OTP Verification with Resend Option
class OTPVerificationApp:
    def __init__(self, root, email):
        self.root = root
        self.email = email
        self.root.title("OTP Verification")
        self.root.geometry("400x300")

        self.otp_label = tk.Label(root, text="Enter the OTP sent to your email:", font=("Arial", 12))
        self.otp_label.pack(pady=10)

        self.otp_entry = tk.Entry(root, font=("Arial", 14))
        self.otp_entry.pack(pady=10)

        self.verify_button = tk.Button(root, text="Verify OTP", font=("Arial", 12), command=self.verify_otp)
        self.verify_button.pack(pady=5)

        # ✅ Resend OTP Button (Initially Disabled)
        self.resend_button = tk.Button(root, text="Resend OTP (Wait 30s)", font=("Arial", 12), state=tk.DISABLED, command=self.resend_otp)
        self.resend_button.pack(pady=5)

        # ✅ Start Timer for Resend OTP Button
        self.start_resend_timer()

    def verify_otp(self):
        entered_otp = self.otp_entry.get()
        if verify_otp(self.email, entered_otp):
            tk.messagebox.showinfo("Success", "✅ OTP Verified Successfully!")
            self.root.destroy()  # ✅ Close OTP window after successful verification
        else:
            tk.messagebox.showerror("Error", "❌ Invalid or Expired OTP. Try Again.")

    def resend_otp(self):
        """✅ Resend OTP and reset the timer."""
        send_otp(self.email)
        self.resend_button.config(text="Resend OTP (Wait 30s)", state=tk.DISABLED)
        self.start_resend_timer()  # Restart 30s Timer

    def start_resend_timer(self):
        """✅ Enable Resend Button after 30 Seconds."""
        def enable_button():
            time.sleep(30)  # Wait for 30 seconds
            self.resend_button.config(text="Resend OTP", state=tk.NORMAL)

        # Run in a separate thread to avoid freezing UI
        Thread(target=enable_button, daemon=True).start()

# ✅ Example Usage:
if __name__ == "__main__":
    root = tk.Tk()
    email = "test@example.com"  # Replace with actual email input from user
    send_otp(email)  # ✅ Send OTP initially
    app = OTPVerificationApp(root, email)
    root.mainloop()
