import os

def actualizar_lista_m3u():
    # Enlace exacto confirmado que funciona perfecto en tu IPTV
    enlace_real_gen = "https://gendigi.net"
    
    archivo_m3u = "listaespanhol.m3u"
    
    if not os.path.exists(archivo_m3u):
        print(f"Error: No se encontró el archivo {archivo_m3u}")
        return

    with open(archivo_m3u, "r", encoding="utf-8") as f:
        lineas = f.readlines()

    modificado = False

    # Buscamos tu etiqueta exacta para modificar la línea correcta (2 posiciones abajo)
    for i in range(len(lineas)):
        if 'tvg-id="Gen.py@SD"' in lineas[i]:
            if i + 2 < len(lineas):
                lineas[i + 2] = enlace_real_gen + "\n"
                modificado = True
                break

    if modificado:
        with open(archivo_m3u, "w", encoding="utf-8") as f:
            f.writelines(lineas)
        print("¡El archivo M3U ha sido asegurado con el enlace de Gendigi con éxito!")
    else:
        print("ERROR: No se encontró la etiqueta tvg-id=\"Gen.py@SD\" en tu archivo.")

if __name__ == "__main__":
    actualizar_lista_m3u()
