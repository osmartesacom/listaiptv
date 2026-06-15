import time
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def extraer_link_gen():
    print("Iniciando Chrome en la nube...")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://gen.com.py")
    
    time.sleep(15)  # Espera a que cargue el reproductor web
    
    link_m3u8 = None
    logs = driver.get_log("performance")
    driver.quit()
    
    # Primero buscamos la playlist principal (master / playlist)
    for entry in logs:
        try:
            log = json.loads(entry["message"])["message"]
            if "Network.requestWillBeSent" in log["method"]:
                params = log.get("params", {})
                request_data = params.get("request", {})
                url = request_data.get("url", "")
                
                # Buscamos que sea un m3u8, que tenga token/llave y que NO sea una chunklist temporal
                if ".m3u8" in url and ("token=" in url or "k=" in url) and "chunklist" not in url:
                    link_m3u8 = url
                    print(f"Playlist principal encontrada: {link_m3u8}")
                    break
        except Exception:
            continue

    # Si por alguna razón no halló la principal, buscamos cualquier m3u8 con llave como respaldo
    if not link_m3u8:
        for entry in logs:
            try:
                log = json.loads(entry["message"])["message"]
                if "Network.requestWillBeSent" in log["method"]:
                    url = log["params"]["request"]["url"]
                    if ".m3u8" in url and ("token=" in url or "k=" in url):
                        link_m3u8 = url
                        break
            except Exception:
                continue
                
    return link_m3u8

def actualizar_lista_m3u(nuevo_enlace):
    if not nuevo_enlace:
        print("No se pudo obtener el token de GEN. Cancelando actualización.")
        return

    archivo_m3u = "listaespanhol.m3u"
    
    if not os.path.exists(archivo_m3u):
        print(f"Error: No se encontró el archivo {archivo_m3u}")
        return

    with open(archivo_m3u, "r", encoding="utf-8") as f:
        lineas = f.readlines()

    modificado = False

    for i in range(len(lineas)):
        if 'tvg-id="Gen.py@SD"' in lineas[i]:
            if i + 2 < len(lineas):
                lineas[i + 2] = nuevo_enlace + "\n"
                modificado = True
                break

    if modificado:
        with open(archivo_m3u, "w", encoding="utf-8") as f:
            f.writelines(lineas)
        print("¡El enlace de GEN ha sido actualizado con la playlist correcta!")
    else:
        print("ERROR: No se encontró la etiqueta tvg-id=\"Gen.py@SD\" en tu archivo.")

if __name__ == "__main__":
    url_capturada = extraer_link_gen()
    actualizar_lista_m3u(url_capturada)
