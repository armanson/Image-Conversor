import os
from PIL import Image, UnidentifiedImageError
from pillow_heif import register_heif_opener
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import time

# Register the HEIF opener for Pillow at application start
register_heif_opener()

class ImageConverterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Image Converter - armanson")
        self.geometry("700x550") # Adjusted for better visualization

        # --- Theme and Color Configuration (New palette: Blue, Yellow, Green) ---
        ctk.set_appearance_mode("System")  # Keep system mode as default
        
        # Custom colors
        self.custom_primary_color = "#1F6AA5"  # Dark Blue (main background)
        self.custom_secondary_color = "#FFD700" # Gold Yellow (buttons, borders, accents)
        self.custom_success_color = "#28A745"   # Green for success/progress

        # Configure main grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) # For the main frame

        # Main frame
        self.main_frame = ctk.CTkFrame(self, fg_color=self.custom_primary_color) # Main blue background
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1) # Central column for elements

        # --- Manual Selection / Click Area ---
        self.select_area_frame = ctk.CTkFrame(self.main_frame, height=150, corner_radius=10,
                                               border_width=3, border_color=self.custom_secondary_color, # Yellow border
                                               fg_color="#3B8ED0") # Lighter blue for the area
        self.select_area_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.select_area_frame.grid_columnconfigure(0, weight=1)
        self.select_area_frame.grid_rowconfigure(0, weight=1)

        self.select_area_label = ctk.CTkLabel(self.select_area_frame, text="Click to select the image to convert",
                                              font=ctk.CTkFont(size=16, weight="bold"), text_color="white")
        self.select_area_label.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.select_area_label.bind("<Button-1>", lambda e: self.select_file()) # A click opens the selector

        # --- Loaded file information ---
        self.file_info_frame = ctk.CTkFrame(self.main_frame, fg_color=self.custom_primary_color)
        self.file_info_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.file_info_frame.grid_columnconfigure(0, weight=1) # Allows the name label to expand
        self.file_info_frame.grid_columnconfigure(1, weight=0) # Maintains the format label size

        self.file_name_label = ctk.CTkLabel(self.file_info_frame, text="No file loaded", font=ctk.CTkFont(size=14),
                                            text_color="white", wraplength=400, anchor="w") # Increased wraplength and anchor
        self.file_name_label.grid(row=0, column=0, padx=10, pady=5, sticky="ew") # sticky="ew" to expand

        self.format_detected_label = ctk.CTkLabel(self.file_info_frame, text="", font=ctk.CTkFont(size=14, weight="bold"),
                                                  text_color=self.custom_secondary_color) # Changed to Yellow!
        self.format_detected_label.grid(row=0, column=1, padx=10, pady=5, sticky="e")

        # --- Output format selection ---
        self.conversion_options_frame = ctk.CTkFrame(self.main_frame, fg_color=self.custom_primary_color)
        self.conversion_options_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.conversion_options_frame.grid_columnconfigure(0, weight=1)
        self.conversion_options_frame.grid_columnconfigure(1, weight=1)

        self.output_format_label = ctk.CTkLabel(self.conversion_options_frame, text="Convert to:", font=ctk.CTkFont(size=14), text_color="white")
        self.output_format_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.output_formats = ["JPG", "JPEG", "PNG", "GIF", "WEBP"]
        self.selected_output_format = ctk.StringVar(value=self.output_formats[0]) # Initial value
        self.output_format_menu = ctk.CTkOptionMenu(self.conversion_options_frame,
                                                  values=self.output_formats,
                                                  variable=self.selected_output_format,
                                                  state="disabled",
                                                  button_color=self.custom_secondary_color, # Yellow menu button
                                                  fg_color=self.custom_secondary_color, # Yellow menu background
                                                  dropdown_fg_color=self.custom_primary_color, # Blue dropdown menu
                                                  dropdown_hover_color=self.custom_success_color, # Green hover
                                                  text_color="black") # Black text for contrast
        self.output_format_menu.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # --- Progress Bar (Styled as "pipeline") ---
        self.progress_container_frame = ctk.CTkFrame(self.main_frame, fg_color=self.custom_primary_color)
        self.progress_container_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        self.progress_container_frame.grid_columnconfigure(0, weight=1) # For the bar
        self.progress_container_frame.grid_columnconfigure(1, weight=0) # For the percentage

        self.progress_bar = ctk.CTkProgressBar(self.progress_container_frame,
                                               height=20,
                                               corner_radius=5,
                                               border_width=2,
                                               border_color=self.custom_secondary_color, # Yellow border for "pipeline"
                                               fg_color="#404040", # Dark background for the "empty pipeline" (simulates black)
                                               progress_color=self.custom_success_color) # Green fill
        self.progress_bar.grid(row=0, column=0, padx=(5, 0), pady=5, sticky="ew") # Right padding for the percentage
        self.progress_bar.set(0)
        self.progress_bar.configure(mode="determinate")

        self.progress_percentage_label = ctk.CTkLabel(self.progress_container_frame, text="0%", font=ctk.CTkFont(size=12, weight="bold"), text_color="white")
        self.progress_percentage_label.grid(row=0, column=1, padx=(5, 5), pady=5, sticky="e") # To the right of the bar

        # --- Action Button (Save File Only) ---
        self.action_buttons_frame = ctk.CTkFrame(self.main_frame, fg_color=self.custom_primary_color)
        self.action_buttons_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        self.action_buttons_frame.grid_columnconfigure(0, weight=1) # Single column for the save button

        self.save_button = ctk.CTkButton(self.action_buttons_frame, text="Save File", command=self.start_save_process, state="disabled",
                                         fg_color=self.custom_secondary_color, # Yellow button
                                         hover_color="#E6B800", # Darker yellow on hover
                                         text_color="black") # Black text
        self.save_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # State variables
        self.current_image_path = None
        self.current_image_obj = None # PIL Image object
        self.conversion_in_progress = False

    def select_file(self):
        """Opens a dialogue to select an image file."""
        if self.conversion_in_progress:
            messagebox.showinfo("Process in Progress", "Please wait for the current conversion to finish.")
            return

        filetypes = [
            ("Image Files", "*.jpg *.jpeg *.png *.gif *.webp *.heic *.heif"),
            ("JPEG Files", "*.jpg *.jpeg"),
            ("PNG Files", "*.png"),
            ("GIF Files", "*.gif"),
            ("WEBP Files", "*.webp"),
            ("HEIF/HEIC Files", "*.heic *.heif"),
            ("All Files", "*.*")
        ]
        file_path = filedialog.askopenfilename(filetypes=filetypes)
        if file_path:
            self.load_image(file_path)

    def load_image(self, file_path):
        """Loads the image, detects its format, and updates the GUI."""
        self.reset_ui() # Reset UI before loading a new image
        self.current_image_path = os.path.normpath(file_path)

        if not os.path.isfile(self.current_image_path):
            messagebox.showerror("File Error", "The specified path does not correspond to a valid file.")
            return

        try:
            img_format = None
            try:
                # Try opening with PIL directly
                with Image.open(self.current_image_path) as img_temp:
                    img_format = img_temp.format.upper()
                self.current_image_obj = Image.open(self.current_image_path)

            except UnidentifiedImageError:
                # If PIL doesn't recognize it, try with pillow_heif if it's a HEIC/HEIF file
                if self.current_image_path.lower().endswith(('.heic', '.heif')):
                    try:
                        self.current_image_obj = Image.open(self.current_image_path)
                        img_format = "HEIC"
                        # Ensure the primary image is loaded if it's HEIC
                        if hasattr(self.current_image_obj, 'info') and self.current_image_obj.info.get("primary", None) is not None:
                            self.current_image_obj.seek(self.current_image_obj.info["primary"])
                        elif hasattr(self.current_image_obj, 'info') and len(self.current_image_obj.info.get("images", [])) > 0:
                            self.current_image_obj.seek(0)
                        else:
                            print("Warning: Could not determine primary image in HEIC file. First available image will be used.")
                    except Exception as heic_e:
                        messagebox.showerror("HEIC Error", f"Could not load HEIC/HEIF file. Details: {heic_e}")
                        self.reset_ui()
                        return
                else:
                    messagebox.showerror("Image Error", "The file is not a recognized image or is corrupt.")
                    self.reset_ui()
                    return
            except Exception as e:
                messagebox.showerror("Load Error", f"An error occurred while loading the image: {e}")
                self.reset_ui()
                return

            if self.current_image_obj:
                base_name = os.path.basename(self.current_image_path)
                self.file_name_label.configure(text=base_name)
                # The detected format color is now yellow (custom_secondary_color)
                self.format_detected_label.configure(text=img_format if img_format else "UNKNOWN", text_color=self.custom_secondary_color)
                self.output_format_menu.configure(state="normal")
                # Enable the save button immediately after loading the image
                self.save_button.configure(state="normal")
                self.progress_bar.set(0) # Reset bar
                self.progress_percentage_label.configure(text="0%")
                self.conversion_in_progress = False # Ensure it's not in progress when loading

        except Exception as e:
            messagebox.showerror("Load Error", f"An unexpected error occurred while loading the image: {e}")
            self.reset_ui()

    def reset_ui(self):
        """Resets the UI elements to their initial state."""
        if self.current_image_obj:
            self.current_image_obj.close() # Release the image resource
            self.current_image_obj = None
        self.current_image_path = None
        self.file_name_label.configure(text="No file loaded")
        self.format_detected_label.configure(text="", text_color=self.custom_secondary_color) # Also resets to yellow
        self.output_format_menu.configure(state="disabled")
        self.save_button.configure(state="disabled")
        self.progress_bar.set(0)
        self.progress_percentage_label.configure(text="0%")
        self.conversion_in_progress = False


    def start_save_process(self):
        """Initiates the conversion simulation process and then saving."""
        if not self.current_image_obj:
            messagebox.showwarning("Warning", "Please load an image first.")
            return
        if self.conversion_in_progress:
            messagebox.showinfo("Process in Progress", "Conversion is already in progress.")
            return

        self.conversion_in_progress = True
        self.save_button.configure(state="disabled") # Disable while simulating conversion
        self.output_format_menu.configure(state="disabled") # Disable menu during conversion
        self.select_area_label.unbind("<Button-1>") # Disable click on selection area
        self.select_area_frame.configure(border_color="gray") # Change border color to indicate disabled

        # Start the progress simulation in a separate thread
        threading.Thread(target=self._simulate_conversion_and_save).start()

    def _simulate_conversion_and_save(self):
        """Simulates conversion progress and then calls save."""
        self.progress_bar.set(0)
        self.progress_percentage_label.configure(text="0%")

        for i in range(101):
            time.sleep(0.02)  # Small pause to simulate work
            self.progress_bar.set(i / 100)
            self.progress_percentage_label.configure(text=f"{i}%")
            self.update_idletasks() # Update UI to see progress

        self.conversion_in_progress = False
        self.save_button.configure(state="normal") # Enable save
        self.output_format_menu.configure(state="normal") # Enable menu
        self.select_area_label.bind("<Button-1>", lambda e: self.select_file()) # Enable click on selection area
        self.select_area_frame.configure(border_color=self.custom_secondary_color) # Revert to original color

        # Once the bar reaches 100%, call the actual saving
        self.save_converted_image()


    def save_converted_image(self):
        """Saves the converted image."""
        if not self.current_image_obj:
            messagebox.showwarning("Warning", "No image to save.")
            return

        output_format = self.selected_output_format.get()
        original_name = os.path.splitext(os.path.basename(self.current_image_path))[0]
        suggested_filename = f"{original_name}_converted.{output_format.lower()}"

        filetypes_save = [
            (f"{output_format} Files", f"*.{output_format.lower()}"),
            ("All Files", "*.*")
        ]

        save_path = filedialog.asksaveasfilename(
            defaultextension=f".{output_format.lower()}",
            filetypes=filetypes_save,
            initialfile=suggested_filename
        )

        if save_path:
            try:
                img_to_save = self.current_image_obj.copy() # Work with a copy to avoid modifying the original in memory

                # Ensure JPG/JPEG do not try to save with alpha channel
                if output_format in ["JPG", "JPEG"] and img_to_save.mode == 'RGBA':
                    img_to_save = img_to_save.convert('RGB')
                # For other cases, ensure a standard color mode if it's not (e.g., grayscale images)
                elif img_to_save.mode not in ['RGB', 'RGBA', 'L', 'P', 'CMYK']:
                     img_to_save = img_to_save.convert('RGB') # Convert to RGB by default for exotic modes

                img_to_save.save(save_path, format=output_format)
                messagebox.showinfo("Success", f"Image successfully saved to:\n{save_path}")
                self.reset_ui() # Reset UI after saving
            except Exception as e:
                messagebox.showerror("Save Error", f"Error saving image! Details: {e}")
        else:
            messagebox.showinfo("Cancelled", "Saving cancelled by user.")


if __name__ == "__main__":
    app = ImageConverterApp()
    app.mainloop()
