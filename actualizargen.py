import time
import json
import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def extraer_tokens_dinamicos():
    print("Iniciando Chrome con emulación móvil de alta compatibilidad...")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Emulamos un dispositivo móvil Android, esto se salta la mayoría de los geobloqueos de Dailymotion
    options.add_argument("--user-agent=Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36")
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # 1. EXTRACCIÓN DE UNICANAL
    enlace_unicanal = None
    try:
        print("Cargando Unicanal...")
        driver.get("https://unicanal.com.py")
        time.sleep(15)
        logs = driver.get_log("performance")
        for entry in logs:
            try:
                log = json.loads(entry["message"])["message"]
                if "Network.requestWillBeSent" in log["method"]:
                    url = log["params"]["request"]["url"]
                    if ".m3u8" in url and ("sec=" in url or "dmcdn.net" in url or "live-" in url):
                        enlace_unicanal = url
                        print("-> Unicanal cazado en logs.")
                        break
            except Exception:
                continue
    except Exception as e:
        print(f"Error en Unicanal: {e}")

    # 2. EXTRACCIÓN DE TRECE
    enlace_trece = None
    try:
        print("Cargando Trece...")
        driver.get("https://trece.com.py")
        time.sleep(15)
        logs = driver.get_log("performance")
        for entry in logs:
            try:
                log = json.loads(entry["message"])["message"]
                if "Network.requestWillBeSent" in log["method"]:
                    url = log["params"]["request"]["url"]
                    if ".m3u8" in url and ("live-" in url or "dmcdn.net" in url or "sec=" in url):
                        enlace_trece = url
                        print("-> Trece cazado en logs.")
                        break
            except Exception:
                continue
    except Exception as e:
        print(f"Error en Trece: {e}")

    # 3. EXTRACCIÓN DE LATELE
    enlace_latele = None
    try:
        print("Cargando LaTele...")
        driver.get("https://latele.com.py")
        time.sleep(15)
        logs = driver.get_log("performance")
        for entry in logs:
            try:
                log = json.loads(entry["message"])["message"]
                if "Network.requestWillBeSent" in log["method"]:
                    url = log["params"]["request"]["url"]
                    if ".m3u8" in url and ("k=" in url or "token=" in url or "desdeparaguay" in url):
                        enlace_latele = url
                        break
            except Exception:
                continue
        
        if enlace_latele and "chunklist_" in enlace_latele:
            enlace_latele = re.sub(r'chunklist_[^/]+\.m3u8', 'playlist.m3u8', enlace_latele)
            print("-> LaTele normalizado.")
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
    enlace_real_gen = "https://gendigi.net"

    for i in range(len(lineas)):
        # 1. Búsqueda flexible de GEN (por ID o por texto de nombre de canal)
        if 'tvg-id="Gen.py@SD"' in lineas[i] or ',Gen' in lineas[i]:
            if i + 2 < len(lineas) and "http" not in lineas[i+2]: # Verifica que estemos modificando el enlace
                lineas[i + 2] = enlace_real_gen + "\n"
                modificado = True
            elif i + 1 < len(lineas) and "http" in lineas[i+1]:
                lineas[i + 1] = enlace_real_gen + "\n"
                modificado = True
                
        # 2. Búsqueda flexible de Unicanal
        if ('tvg-id="Unicanal.py@SD"' in lineas[i] or ',Unicanal' in lineas[i]) and enlace_uni:
            if i + 2 < len(lineas) and "http" not in lineas[i+2]:
                lineas[i + 2] = enlace_uni + "\n"
                modificado = True
            elif i + 1 < len(lineas) and "http" in lineas[i+1]:
                lineas[i + 1] = enlace_uni + "\n"
                modificado = True

        # 3. Búsqueda flexible de Trece
        if ('tvg-id="Trece.py@SD"' in lineas[i] or ',Trece' in lineas[i]) and enlace_tre:
            if i + 2 < len(lineas) and "http" not in lineas[i+2]:
                lineas[i + 2] = enlace_tre + "\n"
                modificado = True
            elif i + 1 < len(lineas) and "http" in lineas[i+1]:
                lineas[i + 1] = enlace_tre + "\n"
                modificado = True

        # 4. Búsqueda flexible de LaTele
        if ('La Tele.py@SD' in lineas[i] or ',La Tele' in lineas[i]) and enlace_lat:
            if i + 2 < len(lineas) and "http" not in lineas[i+2]:
                lineas[i + 2] = enlace_lat + "\n"
                modificado = True
            elif i + 1 < len(lineas) and "http" in lineas[i+1]:
                lineas[i + 1] = enlace_lat + "\n"
                modificado = True

    if modificado:
        with open(archivo_m3u, "w", encoding="utf-8") as f:
            f.writelines(lineas)
        print("¡M3U guardado con éxito con la nueva lógica móvil!")
    else:
        print("ERROR: No se pudo inyectar ninguna coincidencia en las líneas.")

if __name__ == "__main__":
    uni, tre, lat = extraer_tokens_dinamicos()
    actualizar_lista_m3u(uni, tre, lat)
