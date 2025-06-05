# Image-Converter - Creado por armanson

Funcionalidades Principales
Esta herramienta es una aplicación de línea de comandos (CLI/CUI) que te permite convertir tus imágenes entre diversos formatos de manera intuitiva.

Formatos de Imagen Soportados
La herramienta es compatible con los siguientes formatos, tanto para lectura (entrada) como para escritura (salida):

HEIC (¡Sí, incluye los archivos de tu iPhone!)
JPG
JPEG
PNG
GIF
WEBP

Características Destacadas
Detección Automática de Formato: No te preocupes por el formato de entrada, la herramienta lo detecta automáticamente.
Interfaz Intuitiva CLI: A pesar de funcionar en la terminal, te guiará paso a paso con menús numéricos claros y preguntas directas.
Guardado Nativo: Después de la conversión, se abrirá el explorador de archivos de tu sistema operativo (Linux, MacOS, Windows) para que elijas cómodamente dónde guardar tu nueva imagen.
Validación de Entrada: El programa verifica tus selecciones y rutas para asegurar un flujo de trabajo sin interrupciones.

Cómo Usar la Herramienta
Para empezar a usar este conversor de imágenes, sigue estos sencillos pasos.

Primero, asegúrate de tener Git (para clonar el repositorio) y Python 3 instalado en tu sistema.


Configuración y Ejecución por Sistema Operativo

🐧 Linux
1. Instala las dependencias: pip3 install Pillow pillow_heif --> sudo apt-get install python3-tk # Para Debian/Ubuntu y derivados # Si usas Fedora/CentOS: sudo dnf install python3-tkinter
   
2. cd Image_Converter
   
3. Ejecuta la herramienta: python3 Image_Converter.py

🍎 macOS
1. Instala las dependencias: pip3 install Pillow pillow_heif Tkinter (Normalmente, Tkinter ya viene con Python en macOS, pero este comando asegura su disponibilidad.)

2. Ejecuta la herramienta: python3 conversor_imagenes.py
   
🪟 Windows
1. Instala las dependencias: pip3 install Pillow pillow_heif Tkinter (Al igual que en macOS, Tkinter suele estar incluido con Python en Windows.)

2. Ejecuta la herramienta: python conversor_imagenes.py
