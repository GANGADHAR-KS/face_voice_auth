import os
import sys
import subprocess
import pkg_resources

def check_dependencies():
    """Check if all required libraries are installed."""
    required = {
        'opencv-python': 'cv2',
        'face_recognition': 'face_recognition',
        'numpy': 'numpy',
        'sounddevice': 'sounddevice',
        'soundfile': 'soundfile',
        'librosa': 'librosa',
        'pillow': 'PIL'
    }
    
    missing = []
    
    for package, module in required.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    
    return missing

def install_packages(packages):
    """Install missing packages using pip."""
    print(f"Installing missing packages: {', '.join(packages)}")
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"Successfully installed {package}")
        except subprocess.CalledProcessError:
            print(f"Failed to install {package}")

def create_directories():
    """Create necessary directories for the application."""
    dirs = [
        os.path.join("auth_system_data", "faces"),
        os.path.join("auth_system_data", "voices"),
        os.path.join("auth_system_data", "user_files")
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"Created directory: {dir_path}")

def check_camera():
    """Check if a camera is available."""
    try:
        import cv2
        # Try multiple camera indices
        for camera_index in [0, 1, 2]:
            cap = cv2.VideoCapture(camera_index)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    print(f"Camera {camera_index} is working properly.")
                    cap.release()
                    return True
                cap.release()
        
        print("No working camera found. Please check your camera connections and permissions.")
        return False
    except Exception as e:
        print(f"Error checking camera: {str(e)}")
        return False

def check_microphone():
    """Check if a microphone is available."""
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        
        if input_devices:
            print(f"Found {len(input_devices)} input audio devices.")
            return True
        else:
            print("No input audio devices found. Please check your microphone connections.")
            return False
    except Exception as e:
        print(f"Error checking microphone: {str(e)}")
        return False

def main():
    """Main setup function."""
    print("Starting setup for Face and Voice Authentication System...\n")
    
    # Check and install dependencies
    missing_packages = check_dependencies()
    
    if missing_packages:
        print("Missing dependencies detected.")
        install_option = input("Would you like to install missing dependencies now? (y/n): ")
        
        if install_option.lower() == 'y':
            install_packages(missing_packages)
        else:
            print("Please install the following packages manually:")
            for package in missing_packages:
                print(f"  - {package}")
            return
    else:
        print("All required dependencies are installed.")
    
    # Create necessary directories
    create_directories()
    
    # Check hardware
    print("\nChecking hardware components...")
    camera_ok = check_camera()
    mic_ok = check_microphone()
    
    if not camera_ok:
        print("\nWARNING: Camera check failed. The application requires a working camera for face authentication.")
        print("Please check your camera connections and permissions before running the main application.")
    
    if not mic_ok:
        print("\nWARNING: Microphone check failed. The application requires a working microphone for voice authentication.")
        print("Please check your microphone connections before running the main application.")
    
    if camera_ok and mic_ok:
        print("\nSetup complete! All components are working properly.")
        print("You can now run the main application: python face_voice_auth_system.py")
    else:
        print("\nSetup completed with warnings. Please address the issues mentioned above before running the application.")

if __name__ == "__main__":
    main()