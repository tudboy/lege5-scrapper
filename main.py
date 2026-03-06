import os
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import shutil
import re 
from utils import validare_input, sanitize_filename, asteapta_si_muta_redenumit, uneste_pdfuri
from scraper import LegeScraper

# variabila globala in care vom stoca datele din fisierul Excel
df = None

# functia pentru selectarea si incarcarea fisierului Excel
def incarca_fisier():
    global df
    # deschide o fereastra pentru a alege fisierul
    fisier = filedialog.askopenfilename(
        title="Selecteaza un fisier Excel",
        filetypes=[("Fisiere Excel", "*.xlsx;*.xls")]
    )
    if fisier:
        try:
            # citeste fisierul Excel folosind libraria pandas
            df = pd.read_excel(fisier)
            messagebox.showinfo("Succes", f"Fisier incarcat cu succes\n{fisier}")
        except Exception as e:
            messagebox.showerror("Eroare", f"A aparut o eroare la citirea fisierului: {str(e)}")

# functia principala care coordoneaza tot procesul de descarcare
def cauta_legile():
    global df
    
    # validari initiale
    if 'df' not in globals() or df is None:
        messagebox.showerror("Eroare", "Te rog sa incarci mai intai un fisier Excel")
        return
    if not entry_coloana.get().isdigit():
        messagebox.showerror("Eroare", "Te rog introdu un index valid de coloana pentru legi")
        return

    index_coloana = int(entry_coloana.get())
    if index_coloana < 0 or index_coloana >= len(df.columns):
        messagebox.showerror("Eroare", "Index de coloana invalid")
        return

    index_categorie = None
    if entry_categorie.get().isdigit():
        index_categorie = int(entry_categorie.get())
        if index_categorie >= len(df.columns):
            messagebox.showerror("Eroare", "Index de coloana pentru categorie invalid")
            return

    # preluam starea bifelor din interfata
    do_mof = var_mof.get()
    do_modificari = var_modificari.get()
    do_merge = var_merge.get()

    download_temp = None
    scraper = None

    try:
        # convertim toate datele din Excel in format text si extragem coloana cu legi
        df = df.astype(str)
        legi = df.iloc[:, index_coloana].dropna().tolist()

        # pregatim folderul principal si folderul temporar pentru descarcari
        folder_legislatie = "C:\\Lege5"
        os.makedirs(folder_legislatie, exist_ok=True)
        download_temp = os.path.join(folder_legislatie, "TEMP")
        os.makedirs(download_temp, exist_ok=True)

        # pornirea browserului
        scraper = LegeScraper(download_temp)
        
        if not scraper.login("email_utilizator@domeniu.ro", "parola_utilizator"):
            messagebox.showerror("Eroare", "Autentificare esuata")
            scraper.inchide_browser()
            return

        # procesarea fiecarei legi in parte
        for idx, lege_bruta in enumerate(legi):
            # curatam spatiile inutile din numele legii
            lege = re.sub(r'\s+', ' ', str(lege_bruta)).strip()
            
            # sarim peste randurile care contin erori sau sunt goale
            if lege.lower().startswith("error") or lege.lower() == 'nan':
                continue

            # stabilim categoria legii, daca s-a cerut acest lucru in interfata
            if index_categorie is not None and idx < len(df):
                categorie = sanitize_filename(df.iloc[idx, index_categorie], max_length=60)
                if not categorie or categorie.lower() in ["nan", "none"]:
                    categorie = "FaraCategorie"
            else:
                categorie = "Toate"

            # cream folderul categoriei
            categorie_folder_path = os.path.join(folder_legislatie, categorie)
            os.makedirs(categorie_folder_path, exist_ok=True)

            # cream folderul specific legii (curatand inainte numele ca sa fie valid in Windows)
            sanitized_lege_name = sanitize_filename(lege, max_length=120)
            lege_folder_path = os.path.join(categorie_folder_path, sanitized_lege_name)
            os.makedirs(lege_folder_path, exist_ok=True)

            print(f"\nCaut legea: {lege}")
            try:
                # cautam legea si ii salvam adresa web
                url_lege_principala = scraper.cauta_document_si_intra(lege)
                
                # descarcam versiunea Consolidata
                print("Descarc versiunea consolidata")
                try:
                    scraper.apasa_buton_descarcare_standard()
                    asteapta_si_muta_redenumit(lege_folder_path, download_temp, "Lege_consolidata.pdf")
                except Exception as e:
                    print(f"Eroare descarcare lege consolidata: {e}")

                # Descarcam versiunea MOF (Monitorul Oficial)
                are_mof = False
                if do_mof:
                    print("Descarc versiunea MOF")
                    try:
                        scraper.descarca_mof(url_lege_principala)
                        asteapta_si_muta_redenumit(lege_folder_path, download_temp, "Lege_MOF.pdf")
                        are_mof = True
                    except:
                        print("Forma MOF nu este disponibila pentru aceasta lege")
                
                # ne intoarcem la documentul principal in caz ca navigarea ne-a mutat pe alta pagina
                scraper.mergi_la(url_lege_principala)

                # descarcam Anexele
                anexe_pdf_paths = []
                if do_merge:
                    print("\nCaut anexe pentru unire")
                    try:
                        anexe_links = scraper.extrage_linkuri_anexe()
                        if anexe_links:
                            for i, link_anexa in enumerate(anexe_links):
                                try:
                                    scraper.acceseaza_si_descarca_link(link_anexa)
                                    nume_fisier_anexa = f"Anexa_{i+1:02d}.pdf"
                                    # muta anexa din folderul temporar si pastreaza calea pentru unire ulterioara
                                    if asteapta_si_muta_redenumit(lege_folder_path, download_temp, nume_fisier_anexa):
                                        anexe_pdf_paths.append(os.path.join(lege_folder_path, nume_fisier_anexa))
                                except Exception as e:
                                    print(f"Eroare la procesarea anexei: {e}")
                            
                            # revenim iar pe pagina principala dupa descarcarea anexelor
                            scraper.mergi_la(url_lege_principala)
                    except Exception as e:
                        print(f"Eroare la cautarea anexelor: {e}")

                # descarcam modificarile
                mod_folder = None
                if do_modificari:
                    print("Procesez modificarile")
                    modifying_acts_titles = scraper.extrage_titluri_modificari()

                    if modifying_acts_titles:
                        # cream folderul Modificari in interiorul folderului legii
                        mod_folder = os.path.join(lege_folder_path, "Modificari")
                        os.makedirs(mod_folder, exist_ok=True)
                        index_file_path = os.path.join(mod_folder, "_index_modificari.txt")

                        # cautam si descarcam fiecare lege modificatoare
                        for i, title in enumerate(modifying_acts_titles):
                            try:
                                scraper.cauta_document_si_intra(title)
                                scraper.apasa_buton_descarcare_standard()
                                nume_fisier_modificare = f"Modificare_{i+1:02d}.pdf"
                                if asteapta_si_muta_redenumit(mod_folder, download_temp, nume_fisier_modificare):
                                    # adaugam in fisierul text corespondenta intre fisier si titlul legii
                                    with open(index_file_path, 'a', encoding='utf-8') as f:
                                        f.write(f"{nume_fisier_modificare} -> {title}\n")
                            except Exception as e:
                                print(f"Eroare descarcare modificator: {e}")

                # unirea PDF-urilor
                if do_merge:
                    print("Unesc fisierele")
                    
                    # unim versiunea Consolidata cu Anexele ei
                    cale_lege_consolidata = os.path.join(lege_folder_path, "Lege_consolidata.pdf")
                    fisiere_pt_consolidat = [cale_lege_consolidata] + anexe_pdf_paths
                    if os.path.exists(cale_lege_consolidata) and len(fisiere_pt_consolidat) >= 1:
                        cale_output_consolidat = os.path.join(lege_folder_path, f"{sanitized_lege_name}_CONSOLIDAT.pdf")
                        uneste_pdfuri(fisiere_pt_consolidat, cale_output_consolidat)
                    
                    # unim versiunea MOF cu Anexele ei (daca MOF-ul a fost descarcat)
                    cale_lege_mof = os.path.join(lege_folder_path, "Lege_MOF.pdf")
                    if are_mof and os.path.exists(cale_lege_mof):
                        fisiere_pt_mof = [cale_lege_mof] + anexe_pdf_paths
                        if len(fisiere_pt_mof) >= 1:
                            cale_output_mof = os.path.join(lege_folder_path, f"{sanitized_lege_name}_MOF.pdf")
                            uneste_pdfuri(fisiere_pt_mof, cale_output_mof)
                    
                    # stergem fisierele partiale pentru a face curatenie
                    print(" cuurat fisierele individuale (legea principala si anexele)")
                    fisiere_de_sters = [cale_lege_consolidata, cale_lege_mof] + anexe_pdf_paths
                    for fisier in fisiere_de_sters:
                        if os.path.exists(fisier):
                            try:
                                os.remove(fisier)
                            except Exception as e:
                                print(f"Nu s-a putut sterge {fisier}: {e}")
                    print("Curatenie finalizata")

            except Exception as e:
                print(f"Eroare la legea '{lege}': {e}")

        # inchidem procesul Selenium si aratam mesajul de final
        scraper.inchide_browser()
        messagebox.showinfo("Succes", f"Legile s-au descarcat in:\n{folder_legislatie}")

    except Exception as e:
        messagebox.showerror("Eroare", f"A aparut o eroare: {e}")
    finally:
        # la finalizarea tuturor operatiunilor stergem folderul temporar, daca mai exista
        if download_temp and os.path.exists(download_temp):
            try:
                shutil.rmtree(download_temp)
                print(f"Folderul temporar '{download_temp}' a fost sters.")
            except Exception as e:
                print(f"Nu s-a putut sterge folderul temporar: {e}")


# configurare interfata grafica
# construirea ferestrei programului
root = tk.Tk()
root.title("Cautare Legi")
root.geometry("480x450")

# titlul din fereastra
tk.Label(root, text="Incarca un fisier Excel si cauta legile in lege5.ro").pack(pady=10)

# zona in care scrii numerele pentru coloane
frame_input = tk.Frame(root)
frame_input.pack(pady=5)
tk.Label(frame_input, text="Index coloana legi (0, 1, 2...):").grid(row=0, column=0, padx=5, sticky="w")
entry_coloana = tk.Entry(frame_input, validate="key", validatecommand=(root.register(validare_input), "%P"))
entry_coloana.grid(row=0, column=1, padx=5)

tk.Label(frame_input, text="Index coloana categorie (optional):").grid(row=1, column=0, padx=5, sticky="w")
entry_categorie = tk.Entry(frame_input, validate="key", validatecommand=(root.register(validare_input), "%P"))
entry_categorie.grid(row=1, column=1, padx=5)

# zona cu bifele pentru operatiuni suplimentare
frame_optiuni = tk.LabelFrame(root, text="Optiuni de procesare", padx=10, pady=10)
frame_optiuni.pack(pady=10, padx=10, fill="x")

var_mof = tk.BooleanVar(value=True)
var_modificari = tk.BooleanVar(value=True)
var_merge = tk.BooleanVar(value=True)

tk.Checkbutton(frame_optiuni, text="Include forma din Monitorul Oficial (daca exista)", variable=var_mof).pack(anchor="w")
tk.Checkbutton(frame_optiuni, text="Include modificarile", variable=var_modificari).pack(anchor="w")
tk.Checkbutton(frame_optiuni, text="Uneste legea principala cu anexele", variable=var_merge).pack(anchor="w")

# butoanele de executie
tk.Button(root, text="Incarca Excel", command=incarca_fisier).pack(pady=5)
tk.Button(root, text="Cauta Legi", command=cauta_legile).pack(pady=5)
tk.Button(root, text="Inchide", command=root.quit).pack(pady=5)

# bucla principala care tine fereastra deschisa
if __name__ == "__main__":
    root.mainloop()