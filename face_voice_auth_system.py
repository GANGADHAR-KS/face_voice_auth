import os
import pickle
import cv2
import numpy as np
import face_recognition
import sounddevice as sd
import soundfile as sf
import librosa
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import threading
import time
import shutil
from datetime import datetime

class ModernUI(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Secure Authentication System")
        self.geometry("900x600")
        self.configure(bg="#f0f0f0")
        
        # Set application icon
        try:
            self.iconbitmap("icon.ico")
        except:
            pass  # Icon file not found, continue without it
        
        # Initialize variables
        self.current_user = None
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.face_data_dir = os.path.join("auth_system_data", "faces")
        self.voice_data_dir = os.path.join("auth_system_data", "voices")
        self.files_dir = os.path.join("auth_system_data", "user_files")
        
        # Create necessary directories
        for directory in [self.face_data_dir, self.voice_data_dir, self.files_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton', 
                            background='#4CAF50', 
                            foreground='black',
                            font=('Helvetica', 10, 'bold'),
                            padding=10)
        self.style.map('TButton', 
                      background=[('active', '#45a049'), ('disabled', '#cccccc')],
                      foreground=[('active', 'white'), ('disabled', '#666666')])
        self.style.configure('TLabel', 
                            background='#f0f0f0', 
                            font=('Helvetica', 11))
        self.style.configure('Header.TLabel', 
                            font=('Helvetica', 18, 'bold'),
                            background='#f0f0f0')
        self.style.configure('SubHeader.TLabel', 
                            font=('Helvetica', 14),
                            background='#f0f0f0')
        
        # Create and show the login frame
        self.show_login_frame()
        
        # Video capture properties
        self.cap = None
        self.is_capturing = False
        self.camera_thread = None
        
    def show_login_frame(self):
        # Clear any existing frames
        for widget in self.winfo_children():
            widget.destroy()
        
        # Create main frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_label = ttk.Label(main_frame, text="Secure Authentication System", style='Header.TLabel')
        header_label.pack(pady=10)
        
        # Login frame
        login_frame = ttk.Frame(main_frame)
        login_frame.pack(pady=20)
        
        username_label = ttk.Label(login_frame, text="Username:")
        username_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        self.username_entry = ttk.Entry(login_frame, width=30)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        register_btn = ttk.Button(button_frame, text="Register New User", command=self.register_user)
        register_btn.grid(row=0, column=0, padx=10)
        
        login_btn = ttk.Button(button_frame, text="Login", command=self.start_auth)
        login_btn.grid(row=0, column=1, padx=10)
        
        # Footer
        footer_frame = ttk.Frame(main_frame)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        footer_text = ttk.Label(footer_frame, text="© 2025 Secure Authentication System", font=('Helvetica', 8))
        footer_text.pack(side=tk.RIGHT)
    
    def register_user(self):
        username = self.username_entry.get().strip()
        
        if not username:
            messagebox.showerror("Error", "Please enter a username")
            return
            
        # Check if username already exists
        face_path = os.path.join(self.face_data_dir, f"{username}.pkl")
        voice_path = os.path.join(self.voice_data_dir, f"{username}.pkl")
        
        if os.path.exists(face_path) or os.path.exists(voice_path):
            messagebox.showerror("Error", "Username already exists")
            return
            
        self.current_user = username
        self.start_registration()
    
    def start_registration(self):
        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()
            
        # Create registration frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        header_label = ttk.Label(main_frame, text=f"Registration for {self.current_user}", style='Header.TLabel')
        header_label.pack(pady=10)
        
        # Instructions
        instructions = ttk.Label(main_frame, text="We'll capture your face and voice for authentication.", style='SubHeader.TLabel')
        instructions.pack(pady=10)
        
        # Camera frame
        self.camera_frame = ttk.Frame(main_frame, width=500, height=375)
        self.camera_frame.pack(pady=20)
        
        self.camera_label = ttk.Label(self.camera_frame)
        self.camera_label.pack()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        self.face_capture_btn = ttk.Button(button_frame, text="Capture Face", command=self.start_face_capture)
        self.face_capture_btn.grid(row=0, column=0, padx=10)
        
        self.voice_capture_btn = ttk.Button(button_frame, text="Record Voice", command=self.start_voice_capture)
        self.voice_capture_btn.grid(row=0, column=1, padx=10)
        self.voice_capture_btn.config(state='disabled')
        
        self.complete_btn = ttk.Button(button_frame, text="Complete Registration", command=self.complete_registration)
        self.complete_btn.grid(row=0, column=2, padx=10)
        self.complete_btn.config(state='disabled')
        
        back_btn = ttk.Button(main_frame, text="Cancel", command=self.show_login_frame)
        back_btn.pack(pady=10, side=tk.RIGHT)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready to begin registration")
        self.status_label.pack(pady=10)
        
    def start_face_capture(self):
        self.status_label.config(text="Initializing camera...")
        
        # Try multiple camera indices
        self.cap = None
        
        # Try to open the front camera (usually index 0 or 1)
        for camera_index in [0, 1, 2]:
            try:
                temp_cap = cv2.VideoCapture(camera_index)
                if temp_cap.isOpened():
                    # Test if we can actually read a frame
                    ret, _ = temp_cap.read()
                    if ret:
                        self.cap = temp_cap
                        self.camera_index = camera_index
                        self.status_label.config(text=f"Camera {camera_index} opened successfully")
                        break
                    else:
                        temp_cap.release()
            except Exception as e:
                print(f"Error trying camera {camera_index}: {str(e)}")
                
        if self.cap is None:
            messagebox.showerror("Error", "Could not open any camera. Please check your camera connections and permissions.")
            self.status_label.config(text="Camera initialization failed")
            return
        
        # Set camera properties for better quality
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        self.is_capturing = True
        self.face_embeddings = []
        self.face_capture_btn.config(text="Capturing...", state='disabled')
        
        # Start camera in a separate thread
        self.camera_thread = threading.Thread(target=self.capture_face)
        self.camera_thread.daemon = True
        self.camera_thread.start()
    
    def capture_face(self):
        capture_count = 0
        max_captures = 5
        processing = False
        
        while self.is_capturing and capture_count < max_captures:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    continue
                
                # Flip horizontally for a mirror effect
                frame = cv2.flip(frame, 1)
                
                # Convert to RGB for face_recognition
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Display the frame
                img = Image.fromarray(rgb_frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.camera_label.imgtk = imgtk
                self.camera_label.config(image=imgtk)
                self.update()
                
                # Process every few frames to avoid high CPU usage
                if not processing and capture_count < max_captures:
                    processing = True
                    
                    # Detect faces
                    face_locations = face_recognition.face_locations(rgb_frame)
                    
                    if face_locations:
                        # Get face encodings
                        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                        
                        if face_encodings:
                            self.face_embeddings.append(face_encodings[0])
                            capture_count += 1
                            self.status_label.config(text=f"Captured face {capture_count}/{max_captures}")
                    
                    processing = False
                
                time.sleep(0.1)  # Small delay to reduce CPU usage

            except Exception as e:
                print(f"Error in face capture: {str(e)}")
                self.status_label.config(text=f"Error: {str(e)}")
                break
    
        # Cleanup
        if self.cap:
            self.cap.release()
        self.is_capturing = False
        
        if capture_count >= max_captures:
            self.status_label.config(text="Face capture completed successfully")
            self.face_capture_btn.config(text="Face Captured ✓", state='disabled')
            self.voice_capture_btn.config(state='normal')
        else:
            self.status_label.config(text=f"Face capture incomplete ({capture_count}/{max_captures})")
            self.face_capture_btn.config(text="Retry Face Capture", state='normal')

    
    def start_voice_capture(self):
        self.status_label.config(text="Please prepare to record your voice...")
        self.voice_capture_btn.config(state='disabled')
        
        # Ask the user to speak a passphrase
        self.passphrase = "My voice is my password"
        
        messagebox.showinfo("Voice Recording", 
                            f"Please speak the following passphrase clearly after clicking OK:\n\n\"{self.passphrase}\"")
        
        self.status_label.config(text="Recording voice... Please speak now.")
        
        # Record audio in a separate thread
        threading.Thread(target=self.record_voice).start()
    
    def record_voice(self):
        try:
            # Recording parameters
            sample_rate = 16000
            duration = 5  # seconds
            
            # Record audio
            self.audio_data = sd.rec(int(sample_rate * duration), 
                                     samplerate=sample_rate, 
                                     channels=1, 
                                     dtype='float32')
            sd.wait()  # Wait until recording is finished
            
            # Extract MFCC features
            mfcc_features = librosa.feature.mfcc(y=self.audio_data.flatten(), 
                                               sr=sample_rate,
                                               n_mfcc=13)
            
            # Store the average of MFCCs as voice signature
            self.voice_signature = np.mean(mfcc_features, axis=1)
            
            # Save the audio for verification during login
            temp_voice_file = os.path.join(self.voice_data_dir, f"{self.current_user}_temp.wav")
            sf.write(temp_voice_file, self.audio_data, sample_rate)
            
            self.status_label.config(text="Voice capture completed")
            self.voice_capture_btn.config(text="Voice Captured ✓", state='disabled')
            self.complete_btn.config(state='normal')
            
        except Exception as e:
            self.status_label.config(text=f"Error recording voice: {str(e)}")
            self.voice_capture_btn.config(text="Retry Voice Recording", state='normal')
    
    def complete_registration(self):
        # Save face embeddings
        if hasattr(self, 'face_embeddings') and self.face_embeddings:
            face_file = os.path.join(self.face_data_dir, f"{self.current_user}.pkl")
            with open(face_file, 'wb') as f:
                pickle.dump(self.face_embeddings, f)
        else:
            messagebox.showerror("Error", "Face data is missing. Please capture your face again.")
            return
        
        # Save voice signature
        if hasattr(self, 'voice_signature') and self.voice_signature is not None:
            voice_file = os.path.join(self.voice_data_dir, f"{self.current_user}.pkl")
            with open(voice_file, 'wb') as f:
                pickle.dump({"signature": self.voice_signature, "passphrase": self.passphrase}, f)
        else:
            messagebox.showerror("Error", "Voice data is missing. Please record your voice again.")
            return
        
        # Create user directory for files
        user_files_dir = os.path.join(self.files_dir, self.current_user)
        os.makedirs(user_files_dir, exist_ok=True)
        
        messagebox.showinfo("Registration Complete", 
                           f"User {self.current_user} registered successfully!\nYou can now log in.")
        
        self.show_login_frame()
    
    def start_auth(self):
        username = self.username_entry.get().strip()
        
        if not username:
            messagebox.showerror("Error", "Please enter a username")
            return
        
        # Check if user exists
        face_path = os.path.join(self.face_data_dir, f"{username}.pkl")
        voice_path = os.path.join(self.voice_data_dir, f"{username}.pkl")
        
        if not os.path.exists(face_path) or not os.path.exists(voice_path):
            messagebox.showerror("Error", "User not registered. Please register first.")
            return
        
        self.current_user = username
        
        # Start authentication process
        self.show_auth_screen()
    
    def show_auth_screen(self):
        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()
            
        # Create authentication frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        header_label = ttk.Label(main_frame, text=f"Authentication for {self.current_user}", style='Header.TLabel')
        header_label.pack(pady=10)
        
        # Instructions
        instructions = ttk.Label(main_frame, text="Please complete both face and voice verification.", style='SubHeader.TLabel')
        instructions.pack(pady=10)
        
        # Status indicators frame
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(pady=10)
        
        self.face_status = ttk.Label(status_frame, text="Face verification: Pending", font=('Helvetica', 10))
        self.face_status.grid(row=0, column=0, padx=10, pady=5)
        
        self.voice_status = ttk.Label(status_frame, text="Voice verification: Pending", font=('Helvetica', 10))
        self.voice_status.grid(row=1, column=0, padx=10, pady=5)
        
        # Camera frame
        self.camera_frame = ttk.Frame(main_frame, width=500, height=375)
        self.camera_frame.pack(pady=20)
        
        self.camera_label = ttk.Label(self.camera_frame)
        self.camera_label.pack()
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        self.face_verify_btn = ttk.Button(button_frame, text="Verify Face", command=self.start_face_verification)
        self.face_verify_btn.grid(row=0, column=0, padx=10)
        
        self.voice_verify_btn = ttk.Button(button_frame, text="Verify Voice", command=self.start_voice_verification)
        self.voice_verify_btn.grid(row=0, column=1, padx=10)
        
        back_btn = ttk.Button(main_frame, text="Back", command=self.show_login_frame)
        back_btn.pack(pady=10, side=tk.RIGHT)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready to begin verification")
        self.status_label.pack(pady=10)
        
        # Load voice passphrase
        try:
            voice_path = os.path.join(self.voice_data_dir, f"{self.current_user}.pkl")
            with open(voice_path, 'rb') as f:
                voice_data = pickle.load(f)
                self.passphrase = voice_data.get("passphrase", "My voice is my password")
        except:
            self.passphrase = "My voice is my password"
    
    def start_face_verification(self):
        self.status_label.config(text="Initializing camera...")
        
        # Try multiple camera indices
        self.cap = None
        
        # Try to open the front camera (usually index 0 or 1)
        for camera_index in [0, 1, 2]:
            try:
                temp_cap = cv2.VideoCapture(camera_index)
                if temp_cap.isOpened():
                    # Test if we can actually read a frame
                    ret, _ = temp_cap.read()
                    if ret:
                        self.cap = temp_cap
                        self.status_label.config(text=f"Camera {camera_index} opened successfully")
                        break
                    else:
                        temp_cap.release()
            except Exception as e:
                print(f"Error trying camera {camera_index}: {str(e)}")
                
        if self.cap is None:
            messagebox.showerror("Error", "Could not open any camera. Please check your camera connections and permissions.")
            self.status_label.config(text="Camera initialization failed")
            return
            
        # Set camera properties for better quality
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        self.is_capturing = True
        self.face_verify_btn.config(text="Verifying...", state='disabled')
        
        # Load stored face embeddings
        try:
            face_path = os.path.join(self.face_data_dir, f"{self.current_user}.pkl")
            with open(face_path, 'rb') as f:
                self.stored_face_embeddings = pickle.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load stored face data: {str(e)}")
            self.face_verify_btn.config(text="Retry Face Verification", state='normal')
            return
        
        # Start camera in a separate thread
        self.camera_thread = threading.Thread(target=self.verify_face)
        self.camera_thread.daemon = True
        self.camera_thread.start()
    
    def verify_face(self):
        verified = False
        verification_attempts = 0
        max_attempts = 20  # Limit verification attempts
        
        while self.is_capturing and verification_attempts < max_attempts:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    continue
                    
                # Flip horizontally for a mirror effect
                frame = cv2.flip(frame, 1)
                
                # Convert to RGB for face_recognition
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                rgb_frame = rgb_frame.astype(np.uint8)
                
                # Display the frame
                img = Image.fromarray(rgb_frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.camera_label.imgtk = imgtk
                self.camera_label.config(image=imgtk)
                self.update()
                
                # Detect faces
                face_locations = face_recognition.face_locations(rgb_frame)
                
                if face_locations:
                    # Draw rectangle around face
                    for (top, right, bottom, left) in face_locations:
                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    
                    # Get face encodings
                    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                    
                    if face_encodings:
                        # Compare with stored embeddings
                        matches = face_recognition.compare_faces(self.stored_face_embeddings, face_encodings[0], tolerance=0.5)
                        
                        if any(matches):
                            verified = True
                            break
                
                verification_attempts += 1
                time.sleep(0.1)  # Small delay to reduce CPU usage
                
            except Exception as e:
                print(f"Error in face verification: {str(e)}")
                self.status_label.config(text=f"Error: {str(e)}")
                break
        
        # Cleanup
        if self.cap:
            self.cap.release()
        self.is_capturing = False
        
        if verified:
            self.face_status.config(text="Face verification: Successful ✓", foreground="green")
            self.face_verify_btn.config(text="Face Verified ✓", state='disabled')
            self.status_label.config(text="Face verification successful")
            self.check_authentication_complete()
        else:
            self.face_status.config(text="Face verification: Failed ✗", foreground="red")
            self.face_verify_btn.config(text="Retry Face Verification", state='normal')
            self.status_label.config(text="Face verification failed")
    
    def start_voice_verification(self):
        self.status_label.config(text="Preparing for voice verification...")
        self.voice_verify_btn.config(state='disabled')
        
        # Show passphrase to speak
        messagebox.showinfo("Voice Verification", 
                           f"Please speak the following passphrase after clicking OK:\n\n\"{self.passphrase}\"")
        
        self.status_label.config(text="Recording voice... Please speak now.")
        
        # Record audio in a separate thread
        threading.Thread(target=self.verify_voice).start()
    
    def verify_voice(self):
        try:
            # Recording parameters
            sample_rate = 16000
            duration = 5  # seconds
            
            # Record audio
            audio_data = sd.rec(int(sample_rate * duration), 
                               samplerate=sample_rate, 
                               channels=1, 
                               dtype='float32')
            sd.wait()  # Wait until recording is finished
            
            # Extract MFCC features
            mfcc_features = librosa.feature.mfcc(y=audio_data.flatten(), 
                                               sr=sample_rate,
                                               n_mfcc=13)
            
            # Convert to voice signature (average of MFCCs)
            voice_signature = np.mean(mfcc_features, axis=1)
            
            # Load stored voice signature
            voice_path = os.path.join(self.voice_data_dir, f"{self.current_user}.pkl")
            with open(voice_path, 'rb') as f:
                voice_data = pickle.load(f)
                stored_signature = voice_data.get("signature")
            
            # Compare voice signatures using Euclidean distance
            if stored_signature is not None:
                distance = np.linalg.norm(voice_signature - stored_signature)
                threshold = 20.0  # Threshold for voice similarity
                
                if distance < threshold:
                    self.voice_status.config(text="Voice verification: Successful ✓", foreground="green")
                    self.voice_verify_btn.config(text="Voice Verified ✓", state='disabled')
                    self.status_label.config(text="Voice verification successful")
                    self.check_authentication_complete()
                else:
                    self.voice_status.config(text="Voice verification: Failed ✗", foreground="red")
                    self.voice_verify_btn.config(text="Retry Voice Verification", state='normal')
                    self.status_label.config(text="Voice verification failed")
            else:
                raise Exception("Stored voice signature not found")
                
        except Exception as e:
            self.status_label.config(text=f"Error verifying voice: {str(e)}")
            self.voice_status.config(text="Voice verification: Failed ✗", foreground="red")
            self.voice_verify_btn.config(text="Retry Voice Verification", state='normal')
    
    def check_authentication_complete(self):
        # Check if both face and voice are verified
        face_verified = self.face_status.cget("text").endswith("✓")
        voice_verified = self.voice_status.cget("text").endswith("✓")
        
        if face_verified and voice_verified:
            self.status_label.config(text="Authentication successful! Loading file manager...")
            
            # Add a short delay before showing the file manager
            self.after(1000, self.show_file_manager)
    
    def show_file_manager(self):
        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()
            
        # Create file manager frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header with welcome message
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=10)
        
        welcome_label = ttk.Label(header_frame, text=f"Welcome, {self.current_user}!", style='Header.TLabel')
        welcome_label.pack(side=tk.LEFT)
        
        logout_btn = ttk.Button(header_frame, text="Logout", command=self.show_login_frame)
        logout_btn.pack(side=tk.RIGHT)
        
        # File management section
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Left panel - File list
        list_frame = ttk.Frame(file_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        list_label = ttk.Label(list_frame, text="Your Files", style='SubHeader.TLabel')
        list_label.pack(anchor=tk.W, pady=5)
        
        # Frame with scrollbar for file list
        list_scroll_frame = ttk.Frame(list_frame)
        list_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview for file list
        columns = ('name', 'size', 'date')
        self.file_tree = ttk.Treeview(list_scroll_frame, columns=columns, show='headings', yscrollcommand=scrollbar.set)
        
        self.file_tree.heading('name', text='Filename')
        self.file_tree.heading('size', text='Size')
        self.file_tree.heading('date', text='Date Modified')
        
        self.file_tree.column('name', width=200)
        self.file_tree.column('size', width=100)
        self.file_tree.column('date', width=150)
        
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_tree.yview)
        
        # Right panel - actions
        action_frame = ttk.Frame(file_frame)
        action_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

        action_label = ttk.Label(action_frame, text="Actions", style='SubHeader.TLabel')
        action_label.pack(anchor=tk.W, pady=5)
        
        upload_btn = ttk.Button(action_frame, text="Upload File", command=self.upload_file)
        upload_btn.pack(fill=tk.X, pady=5)
        
        download_btn = ttk.Button(action_frame, text="Download File", command=self.download_file)
        download_btn.pack(fill=tk.X, pady=5)
        
        delete_btn = ttk.Button(action_frame, text="Delete File", command=self.delete_file)
        delete_btn.pack(fill=tk.X, pady=5)
        
        refresh_btn = ttk.Button(action_frame, text="Refresh List", command=self.refresh_file_list)
        refresh_btn.pack(fill=tk.X, pady=5)
        
        # Status bar
        self.status_bar = ttk.Label(main_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Load file list
        self.refresh_file_list()
    
    def refresh_file_list(self):
        # Clear current list
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        user_files_dir = os.path.join(self.files_dir, self.current_user)
        
        if not os.path.exists(user_files_dir):
            os.makedirs(user_files_dir, exist_ok=True)
        
        try:
            for filename in os.listdir(user_files_dir):
                file_path = os.path.join(user_files_dir, filename)
                if os.path.isfile(file_path):
                    file_size = os.path.getsize(file_path)
                    file_time = os.path.getmtime(file_path)
                    date_modified = datetime.fromtimestamp(file_time).strftime('%Y-%m-%d %H:%M:%S')
                    
                    if file_size < 1024:
                        size_str = f"{file_size} B"
                    elif file_size < 1024 * 1024:
                        size_str = f"{file_size/1024:.1f} KB"
                    else:
                        size_str = f"{file_size/(1024*1024):.1f} MB"
                    
                    self.file_tree.insert('', tk.END, values=(filename, size_str, date_modified))
            self.status_bar.config(text=f"Found {len(self.file_tree.get_children())} files")
        except Exception as e:
            self.status_bar.config(text=f"Error listing files: {str(e)}")
    
    def upload_file(self):
        filetypes = [("All Files", "*.*"), 
                    ("Text Files", "*.txt"), 
                    ("Images", "*.jpg *.jpeg *.png *.gif"), 
                    ("Documents", "*.pdf *.doc *.docx")]
        filepath = filedialog.askopenfilename(title="Select File to Upload", filetypes=filetypes)
        if not filepath:
            return
        
        user_files_dir = os.path.join(self.files_dir, self.current_user)
        destination = os.path.join(user_files_dir, os.path.basename(filepath))
        
        try:
            if os.path.exists(destination):
                overwrite = messagebox.askyesno("File Exists", 
                                               f"File {os.path.basename(filepath)} already exists.\nDo you want to overwrite it?")
                if not overwrite:
                    return
            shutil.copy2(filepath, destination)
            self.status_bar.config(text=f"Uploaded: {os.path.basename(filepath)}")
            self.refresh_file_list()
        except Exception as e:
            messagebox.showerror("Upload Error", f"Failed to upload file: {str(e)}")
            self.status_bar.config(text=f"Upload failed: {str(e)}")
    
    def download_file(self):
        selection = self.file_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a file to download")
            return
        
        file_info = self.file_tree.item(selection[0], 'values')
        filename = file_info[0]
        
        source_path = os.path.join(self.files_dir, self.current_user, filename)
        
        if not os.path.exists(source_path):
            messagebox.showerror("File Not Found", f"File {filename} not found")
            return
        
        filetypes = [("All Files", "*.*")]
        save_path = filedialog.asksaveasfilename(title="Save File As", defaultextension="*.*",
                                                initialfile=filename, filetypes=filetypes)
        if not save_path:
            return
        
        try:
            shutil.copy2(source_path, save_path)
            self.status_bar.config(text=f"Downloaded: {filename}")
        except Exception as e:
            messagebox.showerror("Download Error", f"Failed to download file: {str(e)}")
            self.status_bar.config(text=f"Download failed: {str(e)}")
    
    def delete_file(self):
        selection = self.file_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a file to delete")
            return
        
        file_info = self.file_tree.item(selection[0], 'values')
        filename = file_info[0]
        
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {filename}?")
        if not confirm:
            return
        
        file_path = os.path.join(self.files_dir, self.current_user, filename)
        
        try:
            os.remove(file_path)
            self.status_bar.config(text=f"Deleted: {filename}")
            self.refresh_file_list()
        except Exception as e:
            messagebox.showerror("Delete Error", f"Failed to delete file: {str(e)}")
            self.status_bar.config(text=f"Delete failed: {str(e)}")

if __name__ == "__main__":
    app = ModernUI()
    app.mainloop()

