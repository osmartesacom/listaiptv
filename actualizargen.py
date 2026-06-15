import time
import json
import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def extraer_tokens_dinamicos():
    print("Iniciando Chrome en la nube...")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # 1. EXTRACCIÓN DE UNICANAL
    enlace_unicanal = None
    try:
        print("Navegando a Unicanal...")
        driver.get("https://unicanal.com.py")
        time.sleep(15)
        logs = driver.get_log("performance")
        for entry in logs:
            try:
                log = json.loads(entry["message"])["message"]
                if "Network.requestWillBeSent" in log["method"]:
                    url = log["params"]["request"]["url"]
                    if ".m3u8" in url and ("dmcdn.net" in url or "sec2" in url):
                        enlace_unicanal = url
                        print(f"-> Unicanal conseguido: {enlace_unicanal[:60]}...")
                        break
            except Exception:
                continue
    except Exception as e:
        print(f"Error en Unicanal: {e}")

    # 2. EXTRACCIÓN DE TRECE
    enlace_trece = None
    try:
        print("Navegando a Trece...")
        driver.get("https://trece.com.py")
        time.sleep(15)
        logs = driver.get_log("performance")
        for entry in logs:
            try:
                log = json.loads(entry["message"])["message"]
                if "Network.requestWillBeSent" in log["method"]:
                    url = log["params"]["request"]["url"]
                    if ".m3u8" in url and ("dmcdn.net" in url or "sec2" in url):
                        enlace_trece = url
                        print(f"-> Trece conseguido: {enlace_trece[:60]}...")
                        break
            except Exception:
                continue
    except Exception as e:
        print(f"Error en Trece: {e}")

    # 3. EXTRACCIÓN DE LATELE
    enlace_latele = None
    try:
        print("Navegando a LaTele...")
        driver.get("https://latele.com.py")
        time.sleep(15)
        logs = driver.get_log("performance")
        for entry in logs:
            try:
                log = json.loads(entry["message"])["message"]
                if "Network.requestWillBeSent" in log["method"]:
                    url = log["params"]["request"]["url"]
                    if ".m3u8" in url and ("token=" in url or "k=" in url):
                        enlace_latele = url
                        break
            except Exception:
                continue
        
        # Si capturó un chunklist temporal en LaTele, lo convertimos a playlist maestra
        if enlace_latele and "chunklist_" in enlace_latele:
            enlace_latele = re.sub(r'chunklist_[^/]+\.m3u8', 'playlist.m3u8', enlace_latele)
            print(f"-> LaTele conseguido y corregido a playlist: {enlace_latele[:60]}...")
    except Exception as e:
        print(f"Error en LaTele: {e}")

    driver.quit()
    return enlace_unicanal, enlace_trece, enlace_latele

def actualizar_lista_m3u(enlace_uni, enlace_tre, enlace_lat):
    archivo_m3u = "listaespanhol.m3u"
    
    if not os.path.exists(archivo_m3u):
        print(f"Error: No se encontró el archivo {archivo_m3u}")
        return

    with open(archivo_m3u, "r", encoding="utf-8") as f:
        lineas = f.readlines()

    modificado = False
    
    # URL 100% CORRECTA Y FIJA DE GEN SOLICITADA POR EL USUARIO
    enlace_real_gen = "https://no.gendigi.net/origin-proxy/playlist.m3u8"

    for i in range(len(lineas)):
        # 1. Mantener GEN fijo con la URL larga correcta
        if 'tvg-id="Gen.py@SD"' in lineas[i]:
            if i + 2 < len(lineas):
                lineas[i + 2] = enlace_real_gen + "\n"
                modificado = True
                
        # 2. Inyectar Unicanal dinámico
        if 'tvg-id="Unicanal.py@SD"' in lineas[i] and enlace_uni:
            if i + 2 < len(lineas):
                lineas[i + 2] = enlace_uni + "\n"
                modificado = True

        # 3. Inyectar Trece dinámico
        if 'tvg-id="Trece.py@SD"' in lineas[i] and enlace_tre:
            if i + 2 < len(lineas):
                lineas[i + 2] = enlace_tre + "\n"
                modificado = True

        # 4. Inyectar LaTele dinámico
        if 'tvg-id="La Tele.py@SD"' in lineas[i] and enlace_lat:
            if i + 2 < len(lineas):
                lineas[i + 2] = enlace_lat + "\n"
                modificado = True

    if modificado:
        with open(archivo_m3u, "w", encoding="utf-8") as f:
            f.writelines(lineas)
        print("¡El archivo M3U ha sido actualizado con éxito para los 4 canales!")
    else:
        print("ERROR: No se encontró ninguna de las etiquetas correspondientes en tu archivo.")

if __name__ == "__main__":
    token_uni, token_trece, token_latele = extraer_tokens_dinamicos()
    actualizar_lista_m3u(token_uni, token_trece, token_latele)

