import tkinter as tk
from tkinter import messagebox
from ui.login_frame import LoginFrame
from ui.signup_frame import SignUpFrame
from ui.home_frame import HomeFrame
from database import DatabaseService
from face_service import FaceService

class App(tk.Tk):
    """Main application class that manages the Tkinter window and frame navigation."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Criminal Detection System")
        self.geometry("1280x720")
        self.resizable(False, False)

        # Initialize services
        try:
            self.db_service = DatabaseService()
            self.face_service = FaceService(self.db_service)
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to connect to services: {e}")
            self.destroy()
            return

        # Container for all frames
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # Initialize all frames (pages)
        for F in (LoginFrame, SignUpFrame, HomeFrame):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginFrame")

    def show_frame(self, page_name):
        """Raise the specified frame to the top."""
        frame = self.frames[page_name]
        frame.tkraise()

        if hasattr(frame, 'on_show'):
            frame.on_show()

    def get_db_service(self):
        return self.db_service

    def get_face_service(self):
        return self.face_service

if __name__ == "__main__":
    app = App()
    app.mainloop()
