import time
import json
import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def extraer_tokens_dinamicos():
    print("Iniciando Chrome con evasión de bloqueo regional...")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Truco de red: Fingimos navegar a través de una IP de Paraguay (ueno/tigo/personal)
    # para engañar a los servidores de Dailymotion y DesdeParaguay
    ip_paraguay = "181.123.0.1" 
    
    driver.execute_cdp_cmd("Network.setUserAgentOverride", {
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })

    # 1. EXTRACCIÓN DE UNICANAL
    enlace_unicanal = None
    try:
        print("Cargando Unicanal...")
        driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {"X-Forwarded-For": ip_paraguay, "Client-IP": ip_paraguay}})
        driver.get("https://unicanal.com.py/")
        time.sleep(15)
        logs = driver.get_log("performance")
        for entry in logs:
            try:
                log = json.loads(entry["message"])["message"]
                if "Network.requestWillBeSent" in log["method"]:
                    url = log["params"]["request"]["url"]
                    if ".m3u8" in url and ("dmcdn.net" in url or "sec2" in url):
                        enlace_unicanal = url
                        print("-> Unicanal capturado con éxito.")
                        break
            except Exception:
                continue
    except Exception as e:
        print(f"Error en Unicanal: {e}")

    # 2. EXTRACCIÓN DE TRECE
    enlace_trece = None
    try:
        print("Cargando Trece...")
        driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {"X-Forwarded-For": ip_paraguay, "Client-IP": ip_paraguay}})
        driver.get("https://trece.com.py/")
        time.sleep(15)
        logs = driver.get_log("performance")
        for entry in logs:
            try:
                log = json.loads(entry["message"])["message"]
                if "Network.requestWillBeSent" in log["method"]:
                    url = log["params"]["request"]["url"]
                    if ".m3u8" in url and ("dmcdn.net" in url or "sec2" in url):
                        enlace_trece = url
                        print("-> Trece capturado con éxito.")
                        break
            except Exception:
                continue
    except Exception as e:
        print(f"Error en Trece: {e}")

    # 3. EXTRACCIÓN DE LATELE
    enlace_latele = None
    try:
        print("Cargando LaTele...")
        driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {"X-Forwarded-For": ip_paraguay, "Client-IP": ip_paraguay}})
        driver.get("https://www.latele.com.py/")
        time.sleep(15)
        logs = driver.get_log("performance")
        for entry in logs:
            try:
                log = json.loads(entry["message"])["message"]
                if "Network.requestWillBeSent" in log["method"]:
                    url = log["params"]["request"]["url"]
                    if ".m3u8" in url and ("token=" in url or "k=" in url or "desdeparaguay" in url):
                        enlace_latele = url
                        break
            except Exception:
                continue
        
        # Forzar conversión a playlist maestra si trae un fragmento temporal
        if enlace_latele and "chunklist_" in enlace_latele:
            enlace_latele = re.sub(r'chunklist_[^/]+\.m3u8', 'playlist.m3u8', enlace_latele)
            print("-> LaTele capturado y normalizado.")
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
    
    # Tu enlace 100% verificado y correcto para GEN
    enlace_real_gen = "https://gendigi.net"

    for i in range(len(lineas)):
        # 1. Mantener tu GEN fijo con la URL larga intacta
        if 'tvg-id="Gen.py@SD"' in lineas[i]:
            if i + 2 < len(lineas):
                lineas[i + 2] = enlace_real_gen + "\n"
                modificado = True
                
        # 2. Inyectar Unicanal capturado
        if 'tvg-id="Unicanal.py@SD"' in lineas[i] and enlace_uni:
            if i + 2 < len(lineas):
                lineas[i + 2] = enlace_uni + "\n"
                modificado = True

        # 3. Inyectar Trece capturado
        if 'tvg-id="Trece.py@SD"' in lineas[i] and enlace_tre:
            if i + 2 < len(lineas):
                lineas[i + 2] = enlace_tre + "\n"
                modificado = True

        # 4. Inyectar LaTele capturado
        if 'tvg-id="La Tele.py@SD"' in lineas[i] and enlace_lat:
            if i + 2 < len(lineas):
                lineas[i + 2] = enlace_lat + "\n"
                modificado = True

    if modificado:
        with open(archivo_m3u, "w", encoding="utf-8") as f:
            f.writelines(lineas)
        print("¡M3U guardado con éxito con tokens locales falsificados!")
    else:
        print("ERROR: No se pudo inyectar ninguna línea.")

if __name__ == "__main__":
    uni, tre, lat = extraer_tokens_dinamicos()
    actualizar_lista_m3u(uni, tre, lat)
