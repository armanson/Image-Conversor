## Image-Converter - Created by armanson
A powerful and easy-to-use local image converter designed to transform your photos directly from the terminal. Convert your images quickly and efficiently!

Key Features
This tool is a command-line interface (CLI/CUI) application that lets you intuitively convert your images between various formats.

Supported Image Formats
The tool is compatible with the following formats for both reading (input) and writing (output):

HEIC (Includes files from your iPhone)
JPG
JPEG
PNG
GIF
WEBP

Highlighted Features
Automatic Format Detection: Don't worry about the input format; the tool detects it automatically for you.
Intuitive CLI Interface: Despite running in the terminal, it guides you step-by-step with clear numeric menus and direct questions.
Native Saving: After conversion, your operating system's file explorer (Linux, macOS, Windows) will open, allowing you to conveniently choose where to save your new image.
Input Validation: The program verifies your selections and paths to ensure a smooth workflow.

Setup and Execution by Operating System
🐧 Linux
1. Install dependencies: pip3 install Pillow pillow_heif --> sudo apt-get install python3-tk # For Debian/Ubuntu and derivatives # Or for Fedora/CentOS: sudo dnf install python3-tkinter

2. Navigate to the project directory: cd Image_Converter

3. Run the tool: python3 Image_Converter.py
   
🍎 macOS
1. Install dependencies : pip3 install Pillow pillow_heif Tkinter (Tkinter usually comes pre-installed with Python on macOS, but this command ensures its availability.)

2. Run the tool: python3 Image_Converter.py

🪟 Windows
1. Install dependencies: pip3 install Pillow pillow_heif Tkinter (Similar to macOS, Tkinter is usually included with Python on Windows.)

2. Run the tool: python Image_Converter.py
