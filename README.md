Lege5 Scraper & PDF Manager
Un instrument puternic de automatizare scris in Python, cu interfata grafica (GUI), conceput pentru a descarca, organiza si consolida acte normative de pe platforma Lege5.ro, pe baza unui tabel Excel.

Functionalitati principale
Procesare in masa (Batch Processing): Citeste automat sute de legi dintr-un fisier Excel (.xlsx, .xls) si le proceseaza secvential.

Automatizare Web Integrala: Se autentifica pe site, cauta documentul, navigheaza si declanseaza descarcarile fara interventie umana, folosind Selenium WebDriver.

Descarcare inteligenta a formelor legale:

Forma consolidata a legii (la zi).

Forma oficiala publicata in Monitorul Oficial (MOF).

Anexele documentului (identificate pe baza de cuvinte cheie: norme, proceduri, metodologii, regulamente etc.).

Actele normative modificatoare (istoricul consolidarii).

Consolidare PDF: Uneste automat documentul principal cu anexele sale intr-un singur fisier PDF perfect organizat.

Management avansat de fisiere: Curata automat numele fisierelor de caractere invalide in Windows, organizeaza documentele in foldere logice (pe categorii din Excel) si face curatenie in fisierele temporare dupa imbinare.

Structura Proiectului
Codul este modularizat pentru o mentenanta usoara si separarea responsabilitatilor:

main.py - Punctul de intrare in aplicatie. Gestioneaza interfata grafica (Tkinter), citirea datelor din Excel (Pandas) si coordonarea intregii logici de business.

scraper.py - Motorul de navigare. Contine clasa LegeScraper care controleaza browserul Chrome, se ocupa de autentificare, cautare si manipularea paginilor web.

utils.py - Uneltele de sistem. Contine functii pure pentru manipularea PDF-urilor (pypdf), mutarea fisierelor pe disc (shutil) si validarea textului.

Cerinte preliminare
Pentru a rula aceasta aplicatie, ai nevoie de Python 3.8 sau o versiune mai noua. De asemenea, trebuie instalate urmatoarele biblioteci externe:

Bash

pip install pandas selenium webdriver-manager pypdf openpyxl
Mod de utilizare
Pregatirea datelor: Creeaza un fisier Excel care sa contina pe o coloana numele sau numerele legilor pe care doresti sa le descarci.

Autentificarea: Deschide fisierul main.py si inlocuieste textul de test ("email_utilizator@domeniu.ro" si "parola_utilizator") cu datele tale reale si valide de cont Lege5.

Pornirea aplicatiei: Ruleaza scriptul principal din terminal sau din mediul tau de dezvoltare:

Bash

python main.py
Utilizarea interfetei grafice:

Apasa "Incarca Excel" si alege fisierul pregatit.

Introdu indexul coloanei unde se afla legile (Atentie: numaratoarea incepe de la 0 pentru prima coloana).

(Optional) Introdu indexul coloanei pentru categorii, daca doresti ca folderele sa fie impartite automat in sub-directoare.

Bifeaza optiunile dorite (descarcare MOF, descarcare modificari, unire PDF-uri).

Apasa "Cauta Legi" si asteapta finalizarea procesului.
