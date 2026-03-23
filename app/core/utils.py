import logging
import os
import re
import sys
import io
from PyPDF2 import PdfReader
logger = logging.getLogger("email_organizer")
def clean_html(raw_html):
        # 1. Eliminar etiquetas de estilo y script junto con su contenido
        clean_text = re.sub(r'<(style|script)[^>]*>.*?</\1>', '', raw_html, flags=re.DOTALL | re.IGNORECASE)
        
        # 2. Eliminar todas las demás etiquetas HTML
        clean_text = re.sub(r'<[^>]+>', ' ', clean_text)
        
        # 3. Reemplazar múltiples espacios o saltos de línea por uno solo
        clean_text = re.sub(r'\s+', ' ', clean_text)
        
        # 4. (Opcional) Decodificar entidades comunes como &nbsp; o &amp;
        clean_text = clean_text.replace("&nbsp;", " ").replace("&amp;", "&")
        
        return clean_text.strip()
def get_senders():
        try:
                # 1. Intentar primero la ruta oficial de Render para secretos
                # Render coloca los archivos en /etc/secrets/nombre_archivo
                render_secret_path = os.path.join("/etc", "secrets", "senders.txt")

                if os.path.exists(render_secret_path):
                        file_path = render_secret_path
                else:
                        # 2. Fallback para desarrollo local (tu código original simplificado)
                        base_path = os.path.dirname(os.path.abspath(__file__))
                        file_path = os.path.join(base_path, "senders.txt")
                senders = []
                with open(file_path, "r") as file:
                        for line in file:
                                sender = line.strip()
                                if sender:  # Evita agregar líneas vacías
                                        senders.append(sender)
                return senders
        except FileNotFoundError:
                print(f"Error: No se encontró el archivo en {file_path}")
                return []
        except FileNotFoundError:
                logger.critical("There is no senders.txt file. You have to create one.")
                input("Press any key to exit")
                sys.exit(1)

def read_bytes_pdf(raw_pdf_data):
        try:
                logger.info("Reading bytes and converto to text pdf")
                raw_data = io.BytesIO(raw_pdf_data)
                reader = PdfReader(raw_data)
                texto = ""
                for page in reader.pages:
                        texto += page.extract_text()
                return texto
        except Exception as error:
                logger.error(f"Can't read bytes and convert to text pdf: {error}")