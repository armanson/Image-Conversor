
import os
from PIL import Image, UnidentifiedImageError
from pillow_heif import register_heif_opener
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import time

# Registrar el abridor de HEIF para Pillow al inicio de la aplicación
register_heif_opener()

class ImageConverterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Conversor de Imágenes - armanson")
        self.geometry("700x550") # Ajustado para una mejor visualización

        # --- Configuración de Tema y Colores (Nueva paleta: Azul, Amarillo, Verde) ---
        ctk.set_appearance_mode("System")  # Mantener modo sistema por defecto

        # Colores personalizados
        self.custom_primary_color = "#1F6AA5"  # Azul oscuro (fondo principal)
        self.custom_secondary_color = "#FFD700" # Amarillo oro (botones, bordes, acentos)
        self.custom_success_color = "#28A745"   # Verde para éxito/progreso

        # Configurar la cuadrícula principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) # Para el frame principal

        # Frame principal
        self.main_frame = ctk.CTkFrame(self, fg_color=self.custom_primary_color) # Fondo azul principal
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1) # Columna central para elementos

        # --- Área de Selección Manual / Click ---
        self.select_area_frame = ctk.CTkFrame(self.main_frame, height=150, corner_radius=10,
                                               border_width=3, border_color=self.custom_secondary_color, # Borde amarillo
                                               fg_color="#3B8ED0") # Un azul más claro para el área
        self.select_area_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.select_area_frame.grid_columnconfigure(0, weight=1)
        self.select_area_frame.grid_rowconfigure(0, weight=1)

        self.select_area_label = ctk.CTkLabel(self.select_area_frame, text="Haz click para seleccionar la imagen a convertir",
                                              font=ctk.CTkFont(size=16, weight="bold"), text_color="white")
        self.select_area_label.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.select_area_label.bind("<Button-1>", lambda e: self.select_file()) # Un click abre el selector

        # --- Información del archivo cargado ---
        self.file_info_frame = ctk.CTkFrame(self.main_frame, fg_color=self.custom_primary_color)
        self.file_info_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.file_info_frame.grid_columnconfigure(0, weight=1) # Permite que el label del nombre se expanda
        self.file_info_frame.grid_columnconfigure(1, weight=0) # Mantiene el tamaño del label de formato

        self.file_name_label = ctk.CTkLabel(self.file_info_frame, text="Ningún archivo cargado", font=ctk.CTkFont(size=14),
                                            text_color="white", wraplength=400, anchor="w") # Aumentado wraplength y anchor
        self.file_name_label.grid(row=0, column=0, padx=10, pady=5, sticky="ew") # sticky="ew" para que se expanda

        self.format_detected_label = ctk.CTkLabel(self.file_info_frame, text="", font=ctk.CTkFont(size=14, weight="bold"),
                                                  text_color=self.custom_secondary_color) # ¡Cambiado a Amarillo!
        self.format_detected_label.grid(row=0, column=1, padx=10, pady=5, sticky="e")

        # --- Selección de formato de salida ---
        self.conversion_options_frame = ctk.CTkFrame(self.main_frame, fg_color=self.custom_primary_color)
        self.conversion_options_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.conversion_options_frame.grid_columnconfigure(0, weight=1)
        self.conversion_options_frame.grid_columnconfigure(1, weight=1)

        self.output_format_label = ctk.CTkLabel(self.conversion_options_frame, text="Convertir a:", font=ctk.CTkFont(size=14), text_color="white")
        self.output_format_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.output_formats = ["JPG", "JPEG", "PNG", "GIF", "WEBP"]
        self.selected_output_format = ctk.StringVar(value=self.output_formats[0]) # Valor inicial
        self.output_format_menu = ctk.CTkOptionMenu(self.conversion_options_frame,
                                                  values=self.output_formats,
                                                  variable=self.selected_output_format,
                                                  state="disabled",
                                                  button_color=self.custom_secondary_color, # Botón del menú amarillo
                                                  fg_color=self.custom_secondary_color, # Fondo del menú amarillo
                                                  dropdown_fg_color=self.custom_primary_color, # Menú desplegable azul
                                                  dropdown_hover_color=self.custom_success_color, # Hover verde
                                                  text_color="black") # Texto en negro para contraste
        self.output_format_menu.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # --- Barra de progreso (Estilizada como "tubería") ---
        self.progress_container_frame = ctk.CTkFrame(self.main_frame, fg_color=self.custom_primary_color)
        self.progress_container_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        self.progress_container_frame.grid_columnconfigure(0, weight=1) # Para la barra
        self.progress_container_frame.grid_columnconfigure(1, weight=0) # Para el porcentaje

        self.progress_bar = ctk.CTkProgressBar(self.progress_container_frame,
                                               height=20,
                                               corner_radius=5,
                                               border_width=2,
                                               border_color=self.custom_secondary_color, # Borde amarillo para "tubería"
                                               fg_color="#404040", # Fondo oscuro para la "tubería vacía" (simula negro)
                                               progress_color=self.custom_success_color) # Relleno verde
        self.progress_bar.grid(row=0, column=0, padx=(5, 0), pady=5, sticky="ew") # Margen derecho para el porcentaje
        self.progress_bar.set(0)
        self.progress_bar.configure(mode="determinate")

        self.progress_percentage_label = ctk.CTkLabel(self.progress_container_frame, text="0%", font=ctk.CTkFont(size=12, weight="bold"), text_color="white")
        self.progress_percentage_label.grid(row=0, column=1, padx=(5, 5), pady=5, sticky="e") # A la derecha de la barra

        # --- Botón de acción (Solo Guardar Archivo) ---
        self.action_buttons_frame = ctk.CTkFrame(self.main_frame, fg_color=self.custom_primary_color)
        self.action_buttons_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        self.action_buttons_frame.grid_columnconfigure(0, weight=1) # Unica columna para el botón de guardar

        self.save_button = ctk.CTkButton(self.action_buttons_frame, text="Guardar Archivo", command=self.start_save_process, state="disabled",
                                         fg_color=self.custom_secondary_color, # Botón amarillo
                                         hover_color="#E6B800", # Amarillo más oscuro al pasar el ratón
                                         text_color="black") # Texto en negro
        self.save_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")


        # Variables de estado
        self.current_image_path = None
        self.current_image_obj = None # Objeto PIL Image
        self.conversion_in_progress = False

    def select_file(self):
        """Abre un diálogo para seleccionar un archivo de imagen."""
        if self.conversion_in_progress:
            messagebox.showinfo("Proceso en curso", "Por favor, espera a que la conversión actual finalice.")
            return

        filetypes = [
            ("Archivos de Imagen", "*.jpg *.jpeg *.png *.gif *.webp *.heic *.heif"),
            ("Archivos JPEG", "*.jpg *.jpeg"),
            ("Archivos PNG", "*.png"),
            ("Archivos GIF", "*.gif"),
            ("Archivos WEBP", "*.webp"),
            ("Archivos HEIF/HEIC", "*.heic *.heif"),
            ("Todos los archivos", "*.*")
        ]
        file_path = filedialog.askopenfilename(filetypes=filetypes)
        if file_path:
            self.load_image(file_path)

    def load_image(self, file_path):
        """Carga la imagen, detecta su formato y actualiza la GUI."""
        self.reset_ui() # Resetear la UI antes de cargar una nueva imagen
        self.current_image_path = os.path.normpath(file_path)

        if not os.path.isfile(self.current_image_path):
            messagebox.showerror("Error de Archivo", "La ruta especificada no corresponde a un archivo válido.")
            return

        try:
            img_format = None
            try:
                # Intentar abrir con PIL directamente
                with Image.open(self.current_image_path) as img_temp:
                    img_format = img_temp.format.upper()
                self.current_image_obj = Image.open(self.current_image_path)

            except UnidentifiedImageError:
                # Si PIL no lo reconoce, intentar con pillow_heif si es un archivo HEIC/HEIF
                if self.current_image_path.lower().endswith(('.heic', '.heif')):
                    try:
                        self.current_image_obj = Image.open(self.current_image_path)
                        img_format = "HEIC"
                        # Asegurarse de que se carga la imagen principal si es HEIC
                        if hasattr(self.current_image_obj, 'info') and self.current_image_obj.info.get("primary", None) is not None:
                            self.current_image_obj.seek(self.current_image_obj.info["primary"])
                        elif hasattr(self.current_image_obj, 'info') and len(self.current_image_obj.info.get("images", [])) > 0:
                            self.current_image_obj.seek(0)
                        else:
                            print("Advertencia: No se pudo determinar la imagen principal en el archivo HEIC. Se utilizará la primera imagen disponible.")
                    except Exception as heic_e:
                        messagebox.showerror("Error HEIC", f"No se pudo cargar el archivo HEIC/HEIF. Detalles: {heic_e}")
                        self.reset_ui()
                        return
                else:
                    messagebox.showerror("Error de Imagen", "El archivo no es una imagen reconocida o está corrupto.")
                    self.reset_ui()
                    return
            except Exception as e:
                messagebox.showerror("Error de Carga", f"Ocurrió un error al cargar la imagen: {e}")
                self.reset_ui()
                return

            if self.current_image_obj:
                base_name = os.path.basename(self.current_image_path)
                self.file_name_label.configure(text=base_name)
                # El color del formato detectado ahora es amarillo (custom_secondary_color)
                self.format_detected_label.configure(text=img_format if img_format else "DESCONOCIDO", text_color=self.custom_secondary_color)
                self.output_format_menu.configure(state="normal")
                # Habilitar el botón de guardar inmediatamente después de cargar la imagen
                self.save_button.configure(state="normal")
                self.progress_bar.set(0) # Resetear barra
                self.progress_percentage_label.configure(text="0%")
                self.conversion_in_progress = False # Asegurar que no está en progreso al cargar

        except Exception as e:
            messagebox.showerror("Error de Carga", f"Ocurrió un error inesperado al cargar la imagen: {e}")
            self.reset_ui()

    def reset_ui(self):
        """Resetea los elementos de la UI a su estado inicial."""
        if self.current_image_obj:
            self.current_image_obj.close() # Liberar el recurso de la imagen
            self.current_image_obj = None
        self.current_image_path = None
        self.file_name_label.configure(text="Ningún archivo cargado")
        self.format_detected_label.configure(text="", text_color=self.custom_secondary_color) # También resetea a amarillo
        self.output_format_menu.configure(state="disabled")
        self.save_button.configure(state="disabled")
        self.progress_bar.set(0)
        self.progress_percentage_label.configure(text="0%")
        self.conversion_in_progress = False


    def start_save_process(self):
        """Inicia el proceso de simulación de conversión y luego el guardado."""
        if not self.current_image_obj:
            messagebox.showwarning("Advertencia", "No hay imagen para guardar.")
            return
        if self.conversion_in_progress:
            messagebox.showinfo("Proceso en curso", "La conversión ya está en progreso.")
            return

        self.conversion_in_progress = True
        self.save_button.configure(state="disabled") # Deshabilitar mientras simula conversión
        self.output_format_menu.configure(state="disabled") # Deshabilitar menú durante la conversión
        self.select_area_label.unbind("<Button-1>") # Deshabilitar el clic en el área de selección
        self.select_area_frame.configure(border_color="gray") # Cambiar color del borde para indicar deshabilitado

        # Iniciar la simulación de progreso en un hilo separado
        threading.Thread(target=self._simulate_conversion_and_save).start()

    def _simulate_conversion_and_save(self):
        """Simula el progreso de la conversión y luego llama a guardar."""
        self.progress_bar.set(0)
        self.progress_percentage_label.configure(text="0%")

        for i in range(101):
            time.sleep(0.02)  # Pequeña pausa para simular trabajo
            self.progress_bar.set(i / 100)
            self.progress_percentage_label.configure(text=f"{i}%")
            self.update_idletasks() # Actualizar la UI para ver el progreso

        self.conversion_in_progress = False
        self.save_button.configure(state="normal") # Habilitar guardar
        self.output_format_menu.configure(state="normal") # Habilitar menú
        self.select_area_label.bind("<Button-1>", lambda e: self.select_file()) # Habilitar el clic en el área de selección
        self.select_area_frame.configure(border_color=self.custom_secondary_color) # Volver al color original

        # Una vez que la barra llega al 100%, llamar al guardado real
        self.save_converted_image()


    def save_converted_image(self):
        """Guarda la imagen convertida."""
        if not self.current_image_obj:
            messagebox.showwarning("Advertencia", "No hay imagen para guardar.")
            return

        output_format = self.selected_output_format.get()
        original_name = os.path.splitext(os.path.basename(self.current_image_path))[0]
        suggested_filename = f"{original_name}_convertido.{output_format.lower()}"

        filetypes_save = [
            (f"Archivos {output_format}", f"*.{output_format.lower()}"),
            ("Todos los archivos", "*.*")
        ]

        save_path = filedialog.asksaveasfilename(
            defaultextension=f".{output_format.lower()}",
            filetypes=filetypes_save,
            initialfile=suggested_filename
        )

        if save_path:
            try:
                img_to_save = self.current_image_obj.copy() # Trabajar con una copia para evitar modificar el original en memoria

                # Asegurarse de que JPG/JPEG no intenten guardar con canal alfa
                if output_format in ["JPG", "JPEG"] and img_to_save.mode == 'RGBA':
                    img_to_save = img_to_save.convert('RGB')
                # Para otros casos, asegurar un modo de color estándar si no lo es (ej. imágenes en escala de grises)
                elif img_to_save.mode not in ['RGB', 'RGBA', 'L', 'P', 'CMYK']:
                     img_to_save = img_to_save.convert('RGB') # Convertir a RGB por defecto para modos exóticos

                img_to_save.save(save_path, format=output_format)
                messagebox.showinfo("Éxito", f"¡Imagen guardada exitosamente en:\n{save_path}")
                self.reset_ui() # Resetear la UI después de guardar
            except Exception as e:
                messagebox.showerror("Error al Guardar", f"¡Error al guardar la imagen! Detalles: {e}")
        else:
            messagebox.showinfo("Cancelado", "Guardado cancelado por el usuario.")


if __name__ == "__main__":
    app = ImageConverterApp()
    app.mainloop()
