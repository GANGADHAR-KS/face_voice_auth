from setuptools import setup, find_packages

setup(
    name="face_voice_auth_system",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "opencv-python>=4.7.0",
        "face_recognition>=1.3.0",
        "numpy>=1.24.0",
        "sounddevice>=0.4.5",
        "soundfile>=0.12.1",
        "librosa>=0.10.0",
        "pillow>=9.4.0",
    ],
    author="Gangadhar",
    author_email="gangadharchakravarthi@gmail.com",
    description="A secure authentication system using facial and voice recognition",
    keywords="authentication, security, face recognition, voice recognition",
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Security",
    ],
)