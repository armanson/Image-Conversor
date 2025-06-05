import os
from PIL import Image, UnidentifiedImageError
from pillow_heif import register_heif_opener
import tkinter as tk
from tkinter import filedialog
import sys

# Registrar el abridor de HEIF para Pillow
register_heif_opener()

def limpiar_consola():
    """Limpia la consola para una mejor visualización."""
    os.system('cls' if os.name == 'nt' else 'clear')

def obtener_ruta_archivo_valida():
    """Pide al usuario la ruta completa del archivo y la valida."""
    while True:
        limpiar_consola()
        # --- CAMBIO REALIZADO AQUÍ ---
        print("--- Conversor de Imágenes CLI/CUI - Creado por armanson ---")
        # -----------------------------
        print("\nPara continuar, necesitamos la ruta completa de la imagen que deseas convertir.")
        print("Puedes copiar la ruta desde tu explorador de archivos y pegarla aquí.")
        print("Si la ruta contiene espacios, asegúrate de ponerla entre comillas dobles (Ej: \"C:\\Mi Carpeta\\Mi Foto.jpg\")")
        
        ruta_entrada = input("\nIntroduce la ruta completa de la imagen: ").strip()

        # Eliminar comillas si el usuario las puso, para que os.path.exists funcione correctamente
        if ruta_entrada.startswith('"') and ruta_entrada.endswith('"'):
            ruta_entrada = ruta_entrada[1:-1]
        
        # En Windows, las rutas pueden contener barras invertidas. Normalizarlas.
        ruta_entrada = os.path.normpath(ruta_entrada)

        if not os.path.exists(ruta_entrada):
            print("\n¡Error! La ruta especificada no existe. Asegúrate de que la ruta es correcta.")
            input("Presiona Enter para intentar de nuevo...")
            continue
        
        if not os.path.isfile(ruta_entrada):
            print("\n¡Error! La ruta especificada no corresponde a un archivo válido. Debe ser una imagen.")
            input("Presiona Enter para intentar de nuevo...")
            continue
        
        return ruta_entrada

def detectar_formato(ruta_imagen):
    """Detecta el formato de una imagen."""
    try:
        with Image.open(ruta_imagen) as img:
            return img.format.upper()
    except UnidentifiedImageError:
        # Intentar con pillow_heif si es un archivo HEIC
        try:
            if ruta_imagen.lower().endswith(('.heic', '.heif')):
                # No es necesario importar HeifImageFile aquí si register_heif_opener ya se usó
                # PIL.Image.open debería manejarlo después del registro
                with Image.open(ruta_imagen) as img:
                    return "HEIC"
            return None
        except Exception:
            return None
    except Exception as e:
        print(f"Error al detectar el formato: {e}")
        return None

def mostrar_menu_formatos(formato_actual):
    """Muestra el menú de formatos de conversión y pide la elección."""
    formatos_soportados_map = {
        1: "JPG", 2: "JPEG", 3: "PNG", 4: "GIF", 5: "WEBP", 6: "WEBM", 7: "HEIC"
    }
    
    print(f"\nEl formato actual de la imagen es: {formato_actual if formato_actual else 'Desconocido'}")
    print("¿A qué formato te gustaría convertirla?")
    for num, fmt in formatos_soportados_map.items():
        print(f"{num}. {fmt}")

    while True:
        try:
            eleccion = input("Introduce el número del formato deseado: ").strip()
            if not eleccion.isdigit():
                print("¡Entrada inválida! Por favor, introduce un número.")
                continue
            
            eleccion = int(eleccion)
            if eleccion in formatos_soportados_map:
                return formatos_soportados_map[eleccion]
            else:
                print("¡Opción no válida! Por favor, introduce un número del menú.")
        except ValueError:
            # Ya lo hemos capturado con isdigit(), pero por si acaso.
            print("¡Entrada inválida! Por favor, introduce un número.")

def guardar_archivo_con_dialogo(imagen_convertida, formato_salida):
    """Abre un diálogo nativo del sistema para guardar el archivo."""
    root = tk.Tk()
    root.withdraw() # Oculta la ventana principal de Tkinter

    # Definir las extensiones de archivo según el formato elegido
    extensiones_para_dialogo = {
        "JPG": [("Archivos JPG", "*.jpg")],
        "JPEG": [("Archivos JPEG", "*.jpeg")],
        "PNG": [("Archivos PNG", "*.png")],
        "GIF": [("Archivos GIF", "*.gif")],
        "WEBP": [("Archivos WEBP", "*.webp")],
        # WEBM y HEIC no se guardan directamente con Pillow estándar de esta forma
        "WEBM": [("Archivos WebM", "*.webm")], 
        "HEIC": [("Archivos HEIC", "*.heic")]
    }

    # Intentar obtener la extensión por defecto
    ext_default = extensiones_para_dialogo.get(formato_salida, [("Todos los archivos", "*.*")])

    # Sugerir un nombre de archivo
    nombre_archivo_sugerido = f"imagen_convertida.{formato_salida.lower()}"

    ruta_guardado = filedialog.asksaveasfilename(
        defaultextension=f".{formato_salida.lower()}",
        filetypes=ext_default + [("Todos los archivos", "*.*")], # Añadir "Todos los archivos"
        initialfile=nombre_archivo_sugerido
    )

    if ruta_guardado:
        try:
            # Manejo especial para formatos que Pillow no guarda directamente o requiere librerías adicionales de escritura
            if formato_salida in ["WEBM", "HEIC"]:
                print(f"Atención: La conversión directa a {formato_salida} es compleja o no está completamente soportada para escritura por Pillow.")
                print("La imagen se guardará como PNG o JPG. Por favor, considera usar otra herramienta para la conversión final a WEBM/HEIC si es necesario.")
                
                # Intentar guardar como JPG si es posible, si no, PNG
                if imagen_convertida.mode == 'RGBA': # JPG no soporta alfa
                    imagen_convertida = imagen_convertida.convert('RGB')
                
                formato_alternativo = "JPEG" if imagen_convertida.mode == 'RGB' else "PNG"
                ruta_guardado_alternativa = ruta_guardado.rsplit('.', 1)[0] + "." + formato_alternativo.lower()
                imagen_convertida.save(ruta_guardado_alternativa, format=formato_alternativo)
                print(f"Imagen guardada como {formato_alternativo} en: {ruta_guardado_alternativa}")
                return True
            else:
                # Asegurarse de que JPG/JPEG no intenten guardar con canal alfa
                if formato_salida in ["JPG", "JPEG"] and imagen_convertida.mode == 'RGBA':
                    imagen_convertida = imagen_convertida.convert('RGB')
                imagen_convertida.save(ruta_guardado, format=formato_salida)
                print(f"¡Éxito! Imagen guardada en: {ruta_guardado}")
                return True
        except Exception as e:
            print(f"¡Error al guardar la imagen! Detalles: {e}")
            return False
    else:
        print("Guardado cancelado por el usuario.")
        return False

def main():
    """Función principal del conversor de imágenes."""
    while True:
        ruta_origen = obtener_ruta_archivo_valida()
        
        formato_detectado = detectar_formato(ruta_origen)
        if not formato_detectado:
            print("\n¡Error! No se pudo detectar el formato de la imagen o no es un archivo de imagen válido.")
            input("Presiona Enter para intentar con otra imagen...")
            continue
        
        formato_destino = mostrar_menu_formatos(formato_detectado)
        
        try:
            # Abrir la imagen con PIL
            # Pillow_heif permite que Image.open() abra archivos HEIC/HEIF directamente
            img = Image.open(ruta_origen)
            
            # Las imágenes HEIC pueden tener múltiples imágenes o metadatos
            # Si es HEIC, asegurarse de que se carga la imagen principal
            if formato_detectado == "HEIC":
                # Asegurarse de que la imagen principal sea la cargada
                if hasattr(img, 'info') and img.info.get("primary", None) is not None:
                    img.seek(img.info["primary"])
                elif hasattr(img, 'info') and len(img.info.get("images", [])) > 0:
                    img.seek(0)
                else:
                    print("Advertencia: No se pudo determinar la imagen principal en el archivo HEIC. Se utilizará la primera imagen disponible.")
                    # Continúa, ya que img ya tiene una imagen cargada.

            # Convertir la imagen al modo adecuado antes de guardar si es necesario
            # Por ejemplo, JPG/JPEG no soporta alfa (RGBA)
            if formato_destino in ['JPG', 'JPEG'] and img.mode == 'RGBA':
                img = img.convert('RGB')
            # Para otros casos, asegurar un modo de color estándar si no lo es (ej. imágenes en escala de grises)
            elif img.mode not in ['RGB', 'RGBA', 'L', 'P', 'CMYK']:
                 img = img.convert('RGB') # Convertir a RGB por defecto para modos exóticos

            if not guardar_archivo_con_dialogo(img, formato_destino):
                print("La conversión fue exitosa pero el archivo no pudo ser guardado correctamente.")
            
        except FileNotFoundError:
            print("\n¡Error! Archivo no encontrado. Por favor, verifica la ruta.")
        except UnidentifiedImageError:
            print("\n¡Error! El archivo no es una imagen reconocida o está corrupto.")
        except Exception as e:
            print(f"\n¡Ocurrió un error inesperado durante la conversión o guardado! Detalles: {e}")
        
        opcion = input("\n¿Quieres convertir otra imagen? (s/n): ").lower().strip()
        if opcion != 's':
            print("¡Gracias por usar el conversor! Adiós.")
            sys.exit()

if __name__ == "__main__":
    main()
