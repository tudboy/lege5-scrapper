import os
import time
import glob
import re
import shutil
from pypdf import PdfWriter

# permite doar cifre sau spatiu gol
def validare_input(text):
    return text.isdigit() or text == ""

# functie de curatare a textului
def sanitize_filename(name, max_length):
    s = str(name)
    s = re.sub(r'[\t\n\r\f\v]', ' ', s)
    s = re.sub(r'[\/:*?"<>|]', '_', s)
    s = re.sub(r'\s+', ' ', s).strip()
    # taie numele daca depaseste lungimea maxima setata
    if len(s) > max_length:
        s = s[:max_length].strip()
    return s

# functie care asteapta finalizarea descarcarii in browser si muta fisierul la locatia finala
def asteapta_si_muta_redenumit(destinatie_folder, temp_folder, nume_nou_fisier, timeout=120):
    start_time = time.time()
    
    # repeta verificarea pana cand expira timpul (timeout)
    while time.time() - start_time < timeout:
        # verifica daca exista fisiere in curs de descarcare (.crdownload) si cate PDF-uri sunt
        downloading_files = glob.glob(os.path.join(temp_folder, "*.crdownload"))
        pdf_files = glob.glob(os.path.join(temp_folder, "*.pdf"))

        if pdf_files and not downloading_files:
            time.sleep(1)
            
            # selecteaza cel mai recent descarcat fisier
            latest_file = max(pdf_files, key=os.path.getctime)
            cale_finala = os.path.join(destinatie_folder, nume_nou_fisier)
            
            # incearca mutarea fisierului de 5 ori (in caz ca antivirusul nu ne lasa)
            for i in range(5):
                try:
                    shutil.move(latest_file, cale_finala)
                    print(f"Fisier mutat: {cale_finala}")
                    return True
                except (PermissionError, OSError):
                    print(f"Fisierul este blocat (incercarea {i+1}/5)")
                    time.sleep(2)
            
            # in caz ca nu a mers dupa 5 incercari
            print(f"Nu s-a putut muta fisierul '{latest_file}'")
            return False

        time.sleep(1)
        
    print(f"Timeout: Fisierul nu a fost descarcat complet in {timeout} secunde.")
    return False

# functie care combina mai multe fisiere PDF in ordinea primita, formand un singur fisier
def uneste_pdfuri(lista_fisiere, cale_output):
    try:
        merger = PdfWriter()
        
        # Parcurge fiecare cale de fisier din lista
        for pdf_path in lista_fisiere:
            if os.path.exists(pdf_path):
                merger.append(pdf_path)
            else:
                print(f"Fisierul de unit nu a fost gasit: {pdf_path}")
        
        # Salveaza rezultatul consolidat pe disc
        merger.write(cale_output)
        merger.close()
        print(f"Fisier consolidat creat cu succes: {cale_output}")
        return True
    except Exception as e:
        print(f"Eroare la unirea fisierelor PDF: {e}")
        return False