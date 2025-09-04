import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np

class HomeFrame(tk.Frame):
    """
    Main UI Frame after login. Handles criminal registration and live detection.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f0f0")
        self.controller = controller
        self.face_service = controller.get_face_service()
        self.db_service = controller.get_db_service()
        
        # State variables
        self.captured_image_for_registration = None
        self.detection_running = False
        self.cap = None

        # --- Main Layout ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # --- Left Frame: Detection ---
        detection_frame = tk.LabelFrame(self, text="Live Surveillance", padx=10, pady=10, font=("Arial", 14))
        detection_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.video_label = tk.Label(detection_frame, bg="black")
        self.video_label.pack(expand=True, fill="both")

        detection_controls = tk.Frame(detection_frame)
        detection_controls.pack(pady=10)
        
        self.start_btn = tk.Button(detection_controls, text="Start Detection", command=self.start_detection)
        self.start_btn.pack(side="left", padx=5)
        
        self.stop_btn = tk.Button(detection_controls, text="Stop Detection", command=self.stop_detection, state="disabled")
        self.stop_btn.pack(side="left", padx=5)

        # --- Right Frame: Registration ---
        reg_frame = tk.LabelFrame(self, text="Register New Criminal", padx=10, pady=10, font=("Arial", 14))
        reg_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        tk.Label(reg_frame, text="Name*:").grid(row=0, column=0, sticky="w", pady=2)
        self.name_entry = tk.Entry(reg_frame)
        self.name_entry.grid(row=0, column=1, sticky="ew", pady=2)
        
        tk.Label(reg_frame, text="Father's Name:").grid(row=1, column=0, sticky="w", pady=2)
        self.father_name_entry = tk.Entry(reg_frame)
        self.father_name_entry.grid(row=1, column=1, sticky="ew", pady=2)

        tk.Label(reg_frame, text="Crimes Done:").grid(row=2, column=0, sticky="w", pady=2)
        self.crimes_entry = tk.Entry(reg_frame)
        self.crimes_entry.grid(row=2, column=1, sticky="ew", pady=2)

        upload_btn = tk.Button(reg_frame, text="Upload Photo for Registration", command=self.upload_photo)
        upload_btn.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.photo_preview_label = tk.Label(reg_frame, text="No photo selected", bg="lightgrey", width=20, height=10)
        self.photo_preview_label.grid(row=4, column=0, columnspan=2, pady=5)
        
        register_btn = tk.Button(reg_frame, text="Register Criminal", command=self.register_criminal, bg="#28a745", fg="white")
        register_btn.grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")
        
        logout_btn = tk.Button(self, text="Logout", command=self.logout)
        logout_btn.grid(row=1, column=1, sticky="se", padx=10, pady=10)

    def on_show(self):
        """Called when the frame is shown."""
        self.face_service.load_embeddings_from_db()

    def upload_photo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if not file_path:
            return
            
        try:
            image = cv2.imread(file_path)
            self.captured_image_for_registration = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            img_pil = Image.fromarray(self.captured_image_for_registration)
            img_pil.thumbnail((150, 150))
            self.photo_img = ImageTk.PhotoImage(img_pil)
            self.photo_preview_label.config(image=self.photo_img, text="")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open image file: {e}", parent=self)

    def register_criminal(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Name is a required field.", parent=self)
            return
            
        if self.captured_image_for_registration is None:
            messagebox.showerror("Error", "Please upload a photo for the criminal.", parent=self)
            return

        # 1. Extract face from the uploaded image
        face_img, error = self.face_service.extract_face(self.captured_image_for_registration)
        if error:
            messagebox.showerror("Registration Error", error, parent=self)
            return

        # 2. Get embedding for the face
        embedding, error = self.face_service.get_embedding(face_img)
        if error:
            messagebox.showerror("Registration Error", error, parent=self)
            return

        # 3. Save to database
        try:
            connection = self.db_service.get_connection()
            with connection.cursor() as cursor:
                sql = "INSERT INTO criminals (name, father_name, crimes_done, embedding) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (
                    name,
                    self.father_name_entry.get().strip(),
                    self.crimes_entry.get().strip(),
                    embedding.tobytes()
                ))
            connection.commit()
            connection.close()
            
            # 4. Reload embeddings and show success
            self.face_service.load_embeddings_from_db()
            messagebox.showinfo("Success", f"Criminal '{name}' registered successfully.", parent=self)
            self.clear_registration_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not register criminal: {e}", parent=self)

    def clear_registration_fields(self):
        self.name_entry.delete(0, tk.END)
        self.father_name_entry.delete(0, tk.END)
        self.crimes_entry.delete(0, tk.END)
        self.captured_image_for_registration = None
        self.photo_preview_label.config(image="", text="No photo selected")

    def start_detection(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Camera Error", "Could not open webcam.", parent=self)
            return
        
        self.detection_running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.detect_faces_loop()

    def stop_detection(self):
        self.detection_running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        
        self.video_label.config(image="") # Clear the label
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

    def detect_faces_loop(self):
        if not self.detection_running:
            return

        ret, frame = self.cap.read()
        if not ret:
            self.stop_detection()
            return
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Perform detection
        faces = self.face_service.detector.detect_faces(frame_rgb)
        for face in faces:
            if face['confidence'] < 0.95:
                continue

            x, y, w, h = face['box']
            face_img = frame_rgb[y:y+h, x:x+w]
            
            embedding, _ = self.face_service.get_embedding(face_img)
            if embedding is not None:
                name, distance = self.face_service.search_face(embedding)
                
                color = (0, 255, 0) if name != "Unknown" else (255, 0, 0)
                label = f"{name} ({distance:.2f})"
                
                cv2.rectangle(frame_rgb, (x, y), (x+w, y+h), color, 2)
                cv2.putText(frame_rgb, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        img = Image.fromarray(frame_rgb)
        img.thumbnail((self.video_label.winfo_width(), self.video_label.winfo_height()))
        self.video_img = ImageTk.PhotoImage(image=img)
        self.video_label.config(image=self.video_img)

        self.after(20, self.detect_faces_loop)
        
    def logout(self):
        self.stop_detection()
        self.controller.show_frame("LoginFrame")
