#Romanian version:
# Lege5 Scraper & PDF Manager

Un instrument puternic de automatizare scris in Python, cu interfata grafica (GUI), conceput pentru a descarca, organiza si consolida acte normative de pe platforma Lege5.ro, pe baza unui tabel Excel.

## Functionalitati principale

* **Procesare in masa (Batch Processing):** Citeste automat sute de legi dintr-un fisier Excel (`.xlsx`, `.xls`) si le proceseaza secvential.
* **Automatizare Web Integrala:** Se autentifica pe site, cauta documentul, navigheaza si declanseaza descarcarile fara interventie umana, folosind Selenium WebDriver.
* **Descarcare inteligenta a formelor legale:**
  * Forma consolidata a legii (la zi).
  * Forma oficiala publicata in Monitorul Oficial (MOF).
  * Anexele documentului (identificate pe baza de cuvinte cheie: norme, proceduri, metodologii, regulamente etc.).
  * Actele normative modificatoare (istoricul consolidarii).
* **Consolidare PDF:** Uneste automat documentul principal cu anexele sale intr-un singur fisier PDF perfect organizat.
* **Management avansat de fisiere:** Curata automat numele fisierelor de caractere invalide in Windows, organizeaza documentele in foldere logice (pe categorii din Excel) si face curatenie in fisierele temporare dupa imbinare.

## Structura Proiectului

Codul este modularizat pentru o mentenanta usoara si separarea responsabilitatilor:

* `main.py` - Punctul de intrare in aplicatie. Gestioneaza interfata grafica (Tkinter), citirea datelor din Excel (Pandas) si coordonarea intregii logici de business.
* `scraper.py` - Motorul de navigare. Contine clasa `LegeScraper` care controleaza browserul Chrome, se ocupa de autentificare, cautare si manipularea paginilor web.
* `utils.py` - Uneltele de sistem. Contine functii pure pentru manipularea PDF-urilor (`pypdf`), mutarea fisierelor pe disc (`shutil`) si validarea textului.

## Cerinte preliminare

Pentru a rula aceasta aplicatie, ai nevoie de **Python 3.8** sau o versiune mai noua. De asemenea, trebuie instalate urmatoarele biblioteci externe:

```bash
pip install pandas selenium webdriver-manager pypdf openpyxl
```
#English version:
# Lege5 Scraper & PDF Manager

A powerful automation tool written in Python, featuring a graphical user interface (GUI), designed to download, organize, and consolidate legal acts from the Lege5.ro platform based on an Excel spreadsheet.

## Key Features

* **Batch Processing:** Automatically reads hundreds of laws from an Excel file (`.xlsx`, `.xls`) and processes them sequentially.
* **Full Web Automation:** Authenticates on the site, searches for the document, navigates, and triggers downloads without human intervention, using Selenium WebDriver.
* **Smart Download of Legal Forms:**
  * Consolidated form of the law (up-to-date).
  * Official form published in the Official Gazette (MOF).
  * Document annexes (identified based on keywords: norms, procedures, methodologies, regulations, etc.).
  * Modifying normative acts (consolidation history).
* **PDF Consolidation:** Automatically merges the main document with its annexes into a single, perfectly organized PDF file.
* **Advanced File Management:** Automatically cleans file names of invalid Windows characters, organizes documents into logical folders (by categories from Excel), and cleans up temporary files after merging.

## Project Structure

The code is modularized for easy maintenance and separation of concerns:

* `main.py` - The entry point of the application. Manages the graphical interface (Tkinter), reading data from Excel (Pandas), and coordinates the entire business logic.
* `scraper.py` - The navigation engine. Contains the `LegeScraper` class which controls the Chrome browser, handles authentication, searching, and web page manipulation.
* `utils.py` - System tools. Contains pure functions for PDF manipulation (`pypdf`), moving files on disk (`shutil`), and text validation.

## Prerequisites

To run this application, you need **Python 3.8** or a newer version. Install the required external libraries by running the following command in your terminal:

```bash
pip install pandas selenium webdriver-manager pypdf openpyxl python-dotenv
```
