Face and Voice Authentication System
This project implements a secure authentication system using both facial recognition and voice verification. After successful authentication, users can access a file management system to upload, download, and manage their files.
Features

User registration with face and voice enrollment
Two-factor authentication (face + voice)
Secure file management system
Simple and intuitive GUI interface

Requirements
This project requires the following Python libraries:
opencv-python
face_recognition
numpy
sounddevice
soundfile
librosa
pillow
Installation

Clone or download this repository
Install the required libraries using pip:

bashpip install opencv-python face_recognition numpy sounddevice soundfile librosa pillow
Note: The face_recognition library requires dlib which might need additional setup. Please refer to the face_recognition documentation for installation instructions specific to your operating system.
Usage

Run the application:

bashpython face_voice_auth_system.py

First-time users should register by:

Clicking on the "Register" button
Entering a username
Following the prompts to capture face and voice samples


To login:

Click on the "Login" button
Position your face in front of the camera
When prompted, record your voice passphrase
Upon successful authentication, you'll have access to your personal file storage



How it Works
Face Recognition
The system uses the face_recognition library which is built on top of dlib's facial recognition algorithms. It extracts facial features and creates a unique encoding that can be compared with stored encodings during authentication.
Voice Authentication
Voice authentication is performed using audio feature extraction with librosa. The system extracts Mel-frequency cepstral coefficients (MFCCs) and chroma features from the user's voice, creating a unique voice profile. During authentication, these features are compared with stored profiles to verify the user's identity.
File Management
Once authenticated, users can:

Upload files from their local system
Download files from their secure storage
Delete files they no longer need
View file details including size and modification date

Security Considerations

Face and voice data are stored locally in the application directory
The system uses a two-factor authentication approach for enhanced security
User data is separated into individual directories to maintain privacy

Limitations

The face recognition system works best in good lighting conditions
Background noise can affect voice authentication accuracy
Currently designed for single-user computers
