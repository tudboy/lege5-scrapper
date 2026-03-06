import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# clasa care controleaza browserul (Chrome) pentru a naviga pe Lege5
class LegeScraper:
    def __init__(self, download_dir):
        # configuram optiunile browserului
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("prefs", {
            "download.default_directory": download_dir, # setam folderul unde se descarca PDF-urile
            "download.prompt_for_download": False,      # ascundem fereastra de confirmare a descarcarii
            "plugins.always_open_pdf_externally": True  # fortam Chrome sa descarce PDF-ul fara sa deschida intr-un tab nou
        })
        # dezactivam avertizarile de securitate la descarcare
        chrome_options.add_argument('--safebrowsing-disable-download-protection')

        # instalam automat driverul potrivit si deschidem browserul
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.maximize_window()

    # functie pentru procesul de autentificare pe site
    def login(self, email, parola):
        self.driver.get("https://lege5.ro/")
        time.sleep(3) 
        try:
            # cautam linkul de autentificare si dam click pe el
            self.driver.find_element(By.LINK_TEXT, "Autentificare").click()
            time.sleep(3)
            # introducem datele de logare
            self.driver.find_element(By.ID, "Login_Mail").send_keys(email)
            self.driver.find_element(By.ID, "Login_Password").send_keys(parola, Keys.RETURN)
            time.sleep(5)
            return True
        except:
            return False

    # functie care cauta titlul legii si intra pe primul rezultat gasit
    def cauta_document_si_intra(self, titlu):
        self.driver.get("https://lege5.ro/")
        # scrie in bara de cautare
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, "searched_text"))).send_keys(titlu)
        # apasa butonul de cautare
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "btn-search"))).click()
        # asteapta sa apara lista de rezultate
        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'search-results')]")))

        # identificam primul rezultat valid
        first_result = WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, "(//h3/a[contains(@href, '/App/Document')])[1]")))
        # modificam un atribut ca sa nu se deschida linkul intr-un tab nou
        self.driver.execute_script("arguments[0].removeAttribute('target')", first_result)
        first_result.click()
        time.sleep(8)
        return self.driver.current_url # returneaza adresa web a documentului

    # functie care automatizeaza click-urile pe meniurile de descarcare a PDF-ului
    def apasa_buton_descarcare_standard(self):
        # click pe iconita de download principala
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.link-download.link-principal[data-target="download"]'))).click()
        time.sleep(1)
        # confirmarea descarcarii in fereastra pop-up
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "js-sendDownloadRequest"))).click()

    # functie care cauta si descarca forma de publicare din Monitorul Oficial
    def descarca_mof(self, url_principala):
        self.driver.get(url_principala)
        time.sleep(3)
        # cautam linkul care specifica varianta MOF
        mof_link = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'forma=mof')]")))
        # derulam pagina pana la link pentru a-l face vizibil si apasabil
        self.driver.execute_script("arguments[0].scrollIntoView(true);", mof_link)
        mof_link.click()
        time.sleep(5)
        self.apasa_buton_descarcare_standard()

    # functie care scaneaza documentul pentru a gasi link-uri catre anexe bazate pe cuvinte cheie
    def extrage_linkuri_anexe(self):
        # cautam toate linkurile (a) dintr-un titlu (h4) care contin unul din cuvintele de mai jos
        anexe_xpath = "//h4//a[@target='_blank' and ( \
        contains(., 'METODOLOGIA') or contains(., 'METODOLOGIE') or contains(., 'NORME TEHNICE') or \
        contains(., 'NORME METODOLOGICE') or contains(., 'NORME DE APLICARE') or contains(., 'NORME PRIVIND') or \
        contains(., 'NORME PROCEDURALE') or contains(., 'NORME INTERNE') or contains(., 'NORME SANITARE') or \
        contains(., 'NORME') or contains(., 'PROCEDURĂ') or contains(., 'PROCEDURA') or \
        contains(., 'PROCEDURĂ DE APLICARE') or contains(., 'PROCEDURĂ OPERAȚIONALĂ') or contains(., 'INSTRUCȚIUNI') or \
        contains(., 'INSTRUCȚIUNI TEHNICE') or contains(., 'INSTRUCȚIUNI METODOLOGICE') or contains(., 'REGULAMENT') or \
        contains(., 'REGULAMENT DE APLICARE') or contains(., 'REGULAMENT INTERN') or contains(., 'REGULAMENT TEHNIC') or \
        contains(., 'GHID') or contains(., 'GHIDUL') or contains(., 'STANDARD') or contains(., 'PLAN') or \
        contains(., 'CRITERII') )]"
        
        # extragem elementele de pe pagina pe baza conditiei de mai sus
        anexe_links_elems = self.driver.find_elements(By.XPATH, anexe_xpath)
        # returnam doar adresele URL (href) ale acestor elemente
        return [elem.get_attribute('href') for elem in anexe_links_elems if elem.get_attribute('href')]

    # intra pe adresa specificata si apasa butonul de descarcare
    def acceseaza_si_descarca_link(self, link):
        self.driver.get(link)
        time.sleep(5)
        self.apasa_buton_descarcare_standard()

    # functie care scaneaza documentul pentru a gasi referinte catre actele normative care l-au modificat
    def extrage_titluri_modificari(self):
        modifying_acts_titles = []
        # cautam linkurile specifice "alegeconsolidare" (actiuni de modificare pe site)
        links = self.driver.find_elements(By.CSS_SELECTOR, "a.lp[href*='alegeconsolidare']")
        for link in links:
            # extragem titlul actului normativ vizat
            title = link.get_attribute('title')
            if title: modifying_acts_titles.append(title)
        return modifying_acts_titles

    #functie care inchide browser-ul
    def inchide_browser(self):
        self.driver.quit()
        
    #functie de reincarcare pagina specifica
    def mergi_la(self, url):
        self.driver.get(url)
        time.sleep(5)