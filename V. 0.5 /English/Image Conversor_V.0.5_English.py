import os
from PIL import Image, UnidentifiedImageError
from pillow_heif import register_heif_opener
import tkinter as tk
from tkinter import filedialog
import sys

# Register the HEIF opener for Pillow
register_heif_opener()

def clear_console():
    """Clears the console for better display."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_valid_file_path():
    """Asks the user for the full file path and validates it."""
    while True:
        clear_console()
        # --- CHANGE MADE HERE ---
        print("--- CLI/CUI Image Converter - Created by armanson ---")
        # ------------------------
        print("\nTo continue, we need the full path to the image you want to convert.")
        print("You can copy the path from your file explorer and paste it here.")
        print("If the path contains spaces, be sure to enclose it in double quotes (e.g., \"C:\\My Folder\\My Photo.jpg\")")
        
        input_path = input("\nEnter the full image path: ").strip()

        # Remove quotes if the user added them, so os.path.exists works correctly
        if input_path.startswith('"') and input_path.endswith('"'):
            input_path = input_path[1:-1]
        
        # On Windows, paths might contain backslashes. Normalize them.
        input_path = os.path.normpath(input_path)

        if not os.path.exists(input_path):
            print("\nError! The specified path does not exist. Please ensure the path is correct.")
            input("Press Enter to try again...")
            continue
        
        if not os.path.isfile(input_path):
            print("\nError! The specified path does not correspond to a valid file. It must be an image.")
            input("Press Enter to try again...")
            continue
        
        return input_path

def detect_format(image_path):
    """Detects the format of an image."""
    try:
        with Image.open(image_path) as img:
            return img.format.upper()
    except UnidentifiedImageError:
        # Try with pillow_heif if it's an HEIC file
        try:
            if image_path.lower().endswith(('.heic', '.heif')):
                # No need to import HeifImageFile here if register_heif_opener has already been used
                # PIL.Image.open should handle it after registration
                with Image.open(image_path) as img:
                    return "HEIC"
            return None
        except Exception:
            return None
    except Exception as e:
        print(f"Error detecting format: {e}")
        return None

def show_format_menu(current_format):
    """Displays the conversion format menu and asks for choice."""
    supported_formats_map = {
        1: "JPG", 2: "JPEG", 3: "PNG", 4: "GIF", 5: "WEBP", 6: "WEBM", 7: "HEIC"
    }
    
    print(f"\nThe current image format is: {current_format if current_format else 'Unknown'}")
    print("To which format would you like to convert it?")
    for num, fmt in supported_formats_map.items():
        print(f"{num}. {fmt}")

    while True:
        try:
            choice = input("Enter the number of the desired format: ").strip()
            if not choice.isdigit():
                print("Invalid input! Please enter a number.")
                continue
            
            choice = int(choice)
            if choice in supported_formats_map:
                return supported_formats_map[choice]
            else:
                print("Invalid option! Please enter a number from the menu.")
        except ValueError:
            # Already captured with isdigit(), but just in case.
            print("Invalid input! Please enter a number.")

def save_file_with_dialog(converted_image, output_format):
    """Opens a native system dialog to save the file."""
    root = tk.Tk()
    root.withdraw() # Hides the main Tkinter window

    # Define file extensions based on the chosen format
    extensions_for_dialog = {
        "JPG": [("JPG Files", "*.jpg")],
        "JPEG": [("JPEG Files", "*.jpeg")],
        "PNG": [("PNG Files", "*.png")],
        "GIF": [("GIF Files", "*.gif")],
        "WEBP": [("WEBP Files", "*.webp")],
        # WEBM and HEIC are not directly saved with standard Pillow in this way
        "WEBM": [("WebM Files", "*.webm")], 
        "HEIC": [("HEIC Files", "*.heic")]
    }

    # Try to get the default extension
    default_ext = extensions_for_dialog.get(output_format, [("All Files", "*.*")])

    # Suggest a file name
    suggested_filename = f"converted_image.{output_format.lower()}"

    save_path = filedialog.asksaveasfilename(
        defaultextension=f".{output_format.lower()}",
        filetypes=default_ext + [("All Files", "*.*")], # Add "All Files"
        initialfile=suggested_filename
    )

    if save_path:
        try:
            # Special handling for formats that Pillow doesn't save directly or require additional write libraries
            if output_format in ["WEBM", "HEIC"]:
                print(f"Attention: Direct conversion to {output_format} is complex or not fully supported for writing by Pillow.")
                print("The image will be saved as PNG or JPG. Please consider using another tool for final conversion to WEBM/HEIC if necessary.")
                
                # Try to save as JPG if possible, otherwise PNG
                if converted_image.mode == 'RGBA': # JPG does not support alpha
                    converted_image = converted_image.convert('RGB')
                
                alternative_format = "JPEG" if converted_image.mode == 'RGB' else "PNG"
                alternative_save_path = save_path.rsplit('.', 1)[0] + "." + alternative_format.lower()
                converted_image.save(alternative_save_path, format=alternative_format)
                print(f"Image saved as {alternative_format} in: {alternative_save_path}")
                return True
            else:
                # Ensure JPG/JPEG do not try to save with an alpha channel
                if output_format in ["JPG", "JPEG"] and converted_image.mode == 'RGBA':
                    converted_image = converted_image.convert('RGB')
                converted_image.save(save_path, format=output_format)
                print(f"Success! Image saved to: {save_path}")
                return True
        except Exception as e:
            print(f"Error saving image! Details: {e}")
            return False
    else:
        print("Save cancelled by the user.")
        return False

def main():
    """Main function of the image converter."""
    while True:
        source_path = get_valid_file_path()
        
        detected_format = detect_format(source_path)
        if not detected_format:
            print("\nError! Could not detect image format or it's not a valid image file.")
            input("Press Enter to try another image...")
            continue
        
        destination_format = show_format_menu(detected_format)
        
        try:
            # Open the image with PIL
            # Pillow_heif allows Image.open() to directly open HEIC/HEIF files
            img = Image.open(source_path)
            
            # HEIC images may have multiple images or metadata
            # If it's HEIC, ensure the primary image is loaded
            if detected_format == "HEIC":
                # Ensure the primary image is loaded
                if hasattr(img, 'info') and img.info.get("primary", None) is not None:
                    img.seek(img.info["primary"])
                elif hasattr(img, 'info') and len(img.info.get("images", [])) > 0:
                    img.seek(0)
                else:
                    print("Warning: Could not determine the primary image in the HEIC file. The first available image will be used.")
                    # Continues, as img already has an image loaded.

            # Convert the image to the appropriate mode before saving if necessary
            # For example, JPG/JPEG does not support alpha (RGBA)
            if destination_format in ['JPG', 'JPEG'] and img.mode == 'RGBA':
                img = img.convert('RGB')
            # For other cases, ensure a standard color mode if it's not already (e.g., grayscale images)
            elif img.mode not in ['RGB', 'RGBA', 'L', 'P', 'CMYK']:
                 img = img.convert('RGB') # Convert to RGB by default for exotic modes

            if not save_file_with_dialog(img, destination_format):
                print("Conversion was successful but the file could not be saved correctly.")
            
        except FileNotFoundError:
            print("\nError! File not found. Please check the path.")
        except UnidentifiedImageError:
            print("\nError! The file is not a recognized image or is corrupt.")
        except Exception as e:
            print(f"\nAn unexpected error occurred during conversion or saving! Details: {e}")
        
        option = input("\nDo you want to convert another image? (y/n): ").lower().strip()
        if option != 'y':
            print("Thank you for using the converter! Goodbye.")
            sys.exit()

if __name__ == "__main__":
    main()
