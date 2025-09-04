import tkinter as tk
from tkinter import messagebox
import bcrypt

class LoginFrame(tk.Frame):
    """UI Frame for user login."""
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller

        frame = tk.Frame(self, bg="white")
        frame.place(relx=0.5, rely=0.5, anchor="center", width=400, height=400)

        title = tk.Label(frame, text="Log In", font=("Arial", 25, "bold"), bg="white", fg="black")
        title.pack(pady=20)

        # Email
        email_label = tk.Label(frame, text="Email Address", font=("Arial", 14), bg="white", fg="black")
        email_label.pack(pady=(10, 5))
        self.email_entry = tk.Entry(frame, font=("Arial", 12), bg="#f0f0f0", bd=0, relief="flat")
        self.email_entry.pack(pady=5, padx=40, fill="x")

        # Password
        password_label = tk.Label(frame, text="Password", font=("Arial", 14), bg="white", fg="black")
        password_label.pack(pady=(10, 5))
        self.password_entry = tk.Entry(frame, font=("Arial", 12), bg="#f0f0f0", show="*", bd=0, relief="flat")
        self.password_entry.pack(pady=5, padx=40, fill="x")
        
        # Login Button
        login_button = tk.Button(frame, text="Log In", command=self.login_user, font=("Arial", 14, "bold"),
                                 bg="#007BFF", fg="white", bd=0, relief="flat", activebackground="#0056b3")
        login_button.pack(pady=20, padx=40, fill="x", ipady=5)

        # Sign Up link
        signup_label = tk.Label(frame, text="Don't have an account?", font=("Arial", 10), bg="white")
        signup_label.pack()
        signup_button = tk.Button(frame, text="Create New Account", command=lambda: controller.show_frame("SignUpFrame"),
                                  font=("Arial", 10, "bold underline"), fg="#007BFF", bg="white", bd=0, relief="flat", cursor="hand2")
        signup_button.pack()

    def login_user(self):
        email = self.email_entry.get()
        password = self.password_entry.get().encode('utf-8')

        if not email or not password:
            messagebox.showerror("Error", "All fields are required.", parent=self)
            return
            
        db_service = self.controller.get_db_service()
        try:
            connection = db_service.get_connection()
            with connection.cursor() as cursor:
                cursor.execute("SELECT password FROM users WHERE email = %s", (email,))
                result = cursor.fetchone()
            connection.close()

            if result and bcrypt.checkpw(password, result['password'].encode('utf-8')):
                messagebox.showinfo("Success", "Login successful!", parent=self)
                self.email_entry.delete(0, tk.END)
                self.password_entry.delete(0, tk.END)
                self.controller.show_frame("HomeFrame")
            else:
                messagebox.showerror("Error", "Invalid email or password.", parent=self)
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}", parent=self)
