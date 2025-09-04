# **Criminal Face Detection System**

This project is a desktop application for detecting and registering criminals using face recognition. It features a user authentication system, a registration module for adding new criminals with their photos and details, and a live surveillance mode to identify known individuals from a camera feed.

## **Key Features**

* **User Authentication:** Secure login and registration system for operators.  
* **Criminal Registration:** Add new criminals to the database by uploading one or more photos and filling in their details.  
* **Face Detection:** Uses MTCNN to accurately detect faces in images and video streams.  
* **Face Recognition:** Employs the deepface library with the ArcFace model to generate face embeddings.  
* **High-Speed Search:** Utilizes Facebook AI's FAISS library for efficient similarity search among thousands of face embeddings.  
* **Real-time Detection:** Provides a live camera feed to identify registered criminals in real-time.  
* **Database Storage:** Stores criminal information and face embeddings in a MySQL database.

## **Architecture Overview**

The application is built with Python and the Tkinter library for the graphical user interface. The architecture has been refactored to separate concerns, making it more modular and easier to maintain.

1. **Main Application (main.py):**  
   * The single entry point of the application.  
   * Manages the main Tkinter window and navigation between different views (Login, Sign Up, Home).  
2. **UI Frames (ui/ directory):**  
   * The user interface is broken down into separate Frame classes for each view (e.g., LoginFrame, HomeFrame).  
   * This makes the UI code modular and prevents the creation of multiple Tk() root windows.  
3. **Face Service (face\_service.py):**  
   * A dedicated module that encapsulates all face recognition logic.  
   * Initializes the MTCNN detector, the DeepFace model, and the FAISS index.  
   * Provides clear functions for extracting embeddings and searching for matching faces.  
   * This centralizes the core AI functionality, removing redundant code from UI files.  
4. **Database Service (database.py):**  
   * Manages all interactions with the MySQL database.  
   * Handles creating tables, adding new users/criminals, retrieving data, and managing connections.  
   * This abstracts away the database logic from the rest of the application.  
5. **Configuration (.env):**  
   * Database credentials and other settings are stored in an environment file, separating configuration from code.

## **Summary of Improvements**

* **Bug Fixes:**  
  * Corrected the logic for parsing the output of DeepFace.represent, which was a common point of failure.  
  * Handled database connection errors more gracefully.  
  * Fixed the application flow which previously created multiple, conflicting Tkinter root windows.  
* **Code Structure:**  
  * **Modular Design:** The original code had significant redundancy. The new structure separates UI, database, and face recognition logic into distinct modules.  
  * **Single Entry Point:** The application now runs from a single main.py file, clarifying the startup process.  
  * **Object-Oriented UI:** The UI is built with classes inheriting from tk.Frame, which is a more robust approach than the mixed procedural style used before.  
* **Performance & Maintainability:**  
  * Centralized service initializations (MTCNN, FAISS) prevent reloading these heavy models unnecessarily.  
  * Code is better organized, commented, and easier to debug and extend.

## **Setup and Installation**

### **1\. Prerequisites**

* Python 3.8+  
* MySQL Server

### **2\. Clone the Repository**

git clone \<your-repository-url\>  
cd \<your-repository-directory\>

### **3\. Set up Python Environment**

It is highly recommended to use a virtual environment.  
python \-m venv venv  
source venv/bin/activate  \# On Windows, use \`venv\\Scripts\\activate\`

### **4\. Install Dependencies**

Install all required Python packages using the requirements.txt file.  
pip install \-r requirements.txt

### **5\. Configure Database**

* Create a new database in your MySQL server.  
* Create a .env file in the project root by copying the example:  
  cp .env.example .env

* Edit the .env file with your MySQL database credentials:  
  DB\_HOST=localhost  
  DB\_USER=your\_mysql\_user  
  DB\_PASSWORD=your\_mysql\_password  
  DB\_NAME=your\_database\_name

### **6\. Run the Application**

Execute the main.py script to launch the application. The necessary database tables will be created automatically on the first run.  
python main.py

You can now sign up for a new account and start registering or detecting criminals.