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
                if getattr(sys, 'frozen', False):
                # Ruta base: la carpeta donde está el exe
                        base_path = os.path.dirname(sys.executable)
                else:
                # Ruta base: la carpeta del script
                        base_path = os.path.dirname(os.path.abspath(__file__))
                filePath = os.path.join(base_path, "senders.txt")
                senders = []
                with open(filePath, "r") as file:
                        for line in file:
                                sender = line.strip()
                                senders.append(sender)
                return senders
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