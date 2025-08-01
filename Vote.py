import subprocess
import time
import traceback
import os
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, NoSuchElementException

# === CONFIGURACIÓN ===
URL_ENCUESTA = "https://xoyondo.com/ap/qxp2fpezbtff9n1"
NUM_VOTOS = 5  # Cambia aquí cuántas veces quieres votar
WINDSCRIBE_CLI = r"C:\Program Files\Windscribe\windscribe-cli.exe"  # Ajusta la ruta si es necesario
VERBOSE = False  # True para ver opciones y botones encontrados

# Lista de países/servidores disponibles
SERVIDORES = [
    "france", "germany", "netherlands", "spain", "romania", "switzerland",
    "norway", "poland", "austria", "belgium", "czech", "italy"
]

ultimo_servidor = None  # Para no repetir el mismo país dos veces

# === FUNCIONES DE VPN ===

def conectar_vpn():
    global ultimo_servidor
    servidor = random.choice(SERVIDORES)

    while servidor == ultimo_servidor and len(SERVIDORES) > 1:
        servidor = random.choice(SERVIDORES)

    ultimo_servidor = servidor

    print(f"[VPN] Conectando a Windscribe en {servidor}...")
    subprocess.call([WINDSCRIBE_CLI, "connect", servidor], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)

def desconectar_vpn():
    print("[VPN] Desconectando Windscribe...")
    subprocess.call([WINDSCRIBE_CLI, "disconnect"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# === FUNCIÓN DE VOTACIÓN ===

def votar():
    print("[NAV] Iniciando navegador...")

    # Opciones para navegador silencioso
    os.environ["WDM_LOG_LEVEL"] = "0"
    chrome_options = Options()
    #chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    service = Service()

    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(URL_ENCUESTA)
        time.sleep(1)

        labels = driver.find_elements(By.CSS_SELECTOR, "label.custom-control-label")

        encontrado = False
        for label in labels:
            texto = label.get_attribute("innerText").strip()
            if VERBOSE:
                print("[DEBUG] Opción encontrada:", texto)
            if "Francisco Javier Alarcón Costa" in texto:
                label.click()
                print("[VOTO] Opción seleccionada.")
                encontrado = True
                break

        if not encontrado:
            print("[ERROR] No se encontró la opción deseada.")
            driver.quit()
            return

        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "button"))
        )
        botones = driver.find_elements(By.TAG_NAME, "button")
        clicado = False
        for b in botones:
            texto_btn = b.text.strip().lower()
            if VERBOSE:
                print("[DEBUG] Botón encontrado:", texto_btn)
            if "voto" in texto_btn or "enviar" in texto_btn or "vote" in texto_btn:
                b.click()
                print("[VOTO] Botón clicado:", texto_btn)
                clicado = True
                break

        if not clicado:
            print("[ERROR] No se encontró ningún botón para votar.")
            driver.quit()
            return

        time.sleep(1)

    except Exception as e:
        print("[ERROR] Algo falló:")
        traceback.print_exc()
    finally:
        try:
            driver.quit()
        except:
            pass

# === BUCLE PRINCIPAL ===

for i in range(NUM_VOTOS):
    print(f"\n--- VOTO #{i+1} ---")
    conectar_vpn()
    votar()
    desconectar_vpn()
