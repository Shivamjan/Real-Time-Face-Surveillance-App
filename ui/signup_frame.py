import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import cv2

class SignUpFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#F0F0F0") # Using a light grey background
        self.controller = controller
        self.face_service = controller.face_service
        self.db_service = controller.db_service
        
        self.image_paths = [] # Store paths to multiple images
        self.preview_images = [] # Store PhotoImage objects to prevent garbage collection

        frame = tk.Frame(self, bg="white", highlightbackground="black", highlightthickness=1)
        frame.place(relx=0.5, rely=0.5, anchor="center", width=550, height=650) # Increased height for previews

        title1 = tk.Label(frame, text="Register New Criminal", font=("Arial", 22, "bold"), bg="white", fg="black")
        title1.pack(pady=(20, 5))

        # --- Input Fields ---
        fields_frame = tk.Frame(frame, bg="white")
        fields_frame.pack(pady=15, padx=40, fill="x")

        tk.Label(fields_frame, text="Full Name", font=("Arial", 12), bg="white").grid(row=0, column=0, sticky="w", pady=(10,2))
        self.name_txt = tk.Entry(fields_frame, font=("Arial", 12))
        self.name_txt.grid(row=1, column=0, sticky="ew")

        tk.Label(fields_frame, text="Email", font=("Arial", 12), bg="white").grid(row=2, column=0, sticky="w", pady=(10,2))
        self.email_txt = tk.Entry(fields_frame, font=("Arial", 12))
        self.email_txt.grid(row=3, column=0, sticky="ew")

        tk.Label(fields_frame, text="Password", font=("Arial", 12), bg="white").grid(row=4, column=0, sticky="w", pady=(10,2))
        self.password_txt = tk.Entry(fields_frame, font=("Arial", 12), show="*")
        self.password_txt.grid(row=5, column=0, sticky="ew")

        # --- Photo Selection ---
        photo_frame = tk.Frame(fields_frame, bg="white")
        photo_frame.grid(row=6, column=0, sticky="ew", pady=(15, 5))

        self.photo_button = tk.Button(photo_frame, text="Add a Photo", command=self.add_photo)
        self.photo_button.pack(side="left")
        
        # Clear button for selections
        self.clear_button = tk.Button(photo_frame, text="Clear All", command=self.clear_previews)
        self.clear_button.pack(side="left", padx=10)

        self.photo_status_label = tk.Label(photo_frame, text="0 photos selected", font=("Arial", 10), bg="white", fg="grey")
        self.photo_status_label.pack(side="left", padx=10)
        
        # --- Image Preview Area ---
        self.preview_frame = tk.Frame(fields_frame, bg="#E0E0E0", bd=1, relief="sunken")
        self.preview_frame.grid(row=7, column=0, sticky="ew", pady=10, ipady=5)

        # --- Buttons ---
        self.signup_button = tk.Button(frame, text="Register", command=self.signup_func, font=("Arial", 14, "bold"), bg="#4CAF50", fg="white")
        self.signup_button.pack(pady=20, ipadx=50)
        
        self.back_button = tk.Button(frame, text="Back to Login", command=lambda: controller.show_frame("LoginFrame"))
        self.back_button.pack(pady=(0, 20))

    def add_photo(self):
        """Open file dialog to select a single photo and add it to the list."""
        filepath = filedialog.askopenfilename(
            title="Select a photo",
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        
        if filepath and filepath not in self.image_paths:
            self.image_paths.append(filepath)
            self.update_previews_and_status()
        elif filepath:
            messagebox.showwarning("Duplicate", "This image has already been selected.", parent=self)

    def update_previews_and_status(self):
        """Clears and redraws all previews based on the current image_paths list."""
        # Clear existing preview widgets
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
        
        # Clear the PhotoImage object cache
        self.preview_images = []

        # Update status label
        self.photo_status_label.config(text=f"{len(self.image_paths)} photos selected")

        # Re-display all previews
        for path in self.image_paths:
            try:
                img = Image.open(path)
                img.thumbnail((80, 80))
                photo_img = ImageTk.PhotoImage(img)
                
                self.preview_images.append(photo_img)
                
                preview_label = tk.Label(self.preview_frame, image=photo_img, bg="#E0E0E0")
                preview_label.pack(side="left", padx=5, pady=5)
            except Exception as e:
                print(f"Could not load preview for {path}: {e}")

    def clear_previews(self):
        """Clears all image paths, PhotoImage objects, and thumbnail widgets."""
        self.image_paths = []
        self.update_previews_and_status()

    def signup_func(self):
        """Register criminal using multiple photos to create an average embedding."""
        name = self.name_txt.get()
        email = self.email_txt.get()
        password = self.password_txt.get()

        if not all([name, email, password]):
            messagebox.showerror("Error", "All fields are required.", parent=self)
            return
        
        if len(self.image_paths) == 0:
            messagebox.showerror("Error", "Please add photos for registration.", parent=self)
            return
        
        if len(self.image_paths) < 3:
            if not messagebox.askyesno("Warning", "For best results, we recommend adding at least 3 photos. Do you want to continue anyway?", parent=self):
                return

        try:
            success, message = self.face_service.register_criminal_with_photos(
                name=name,
                email=email,
                password=password,
                image_paths=self.image_paths
            )

            if success:
                messagebox.showinfo("Success", message, parent=self)
                self.controller.show_frame("HomeFrame")
                self.reset_fields()
            else:
                messagebox.showerror("Registration Failed", message, parent=self)

        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=self)
            
    def reset_fields(self):
        self.name_txt.delete(0, tk.END)
        self.email_txt.delete(0, tk.END)
        self.password_txt.delete(0, tk.END)
        self.clear_previews()

