import socket
import pylink
import sys
import time
import os

UDP_IP = "127.0.0.1"
PORT_PYTHON = 5005
EYELINK_IP = "100.1.1.1" 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
carpeta_destino = os.path.join(BASE_DIR, "data")

if not os.path.exists(carpeta_destino):
    os.makedirs(carpeta_destino)

# Configurar Socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((UDP_IP, PORT_PYTHON))
sock.settimeout(0.5)

# Conectar al EyeLink
print(f"Conectando al EyeLink en {EYELINK_IP}...")
try:
    el_tracker = pylink.EyeLink(EYELINK_IP)
    print("Conexión hardware establecida con éxito.")
except RuntimeError as error:
    print(f"Error de conexión con EyeLink: {error}")
    sys.exit()

archivo_abierto = False
EDF_FILENAME = "TEMP.EDF" 
tiempo_ultimo_mensaje = time.time()

print("Servidor listo. Esperando inicio desde Godot...")

try:
    while True:
        # --- DEAD MAN'S SWITCH (HEARTBEAT CHECK) ---
        if time.time() - tiempo_ultimo_mensaje > 4.0:
            print("\n[!] Alerta: Se perdió la conexión con Godot. Iniciando guardado de emergencia...")
            break 

        try:
            data, addr = sock.recvfrom(1024)
            mensaje = data.decode('utf-8').strip()
            
            # Actualizamos el reloj cada vez que nos llega CUALQUIER mensaje
            tiempo_ultimo_mensaje = time.time() 
            
            # Si es el latido, lo ignoramos (no lo anotamos en el EDF)
            if mensaje == "HEARTBEAT":
                continue 

            # 1. Lógica de Conexión y Apertura de Archivo
            if mensaje.startswith("CONNECT:"):
                # Cortamos el ID a máximo 8 caracteres para no romper el EyeLink
                id_sujeto = mensaje.split(":")[1][:8] 
                EDF_FILENAME = f"{id_sujeto}.EDF"
                print(f"Iniciando registro para: {id_sujeto}")
                
                el_tracker.openDataFile(EDF_FILENAME)
                el_tracker.startRecording(1, 1, 1, 1)
                archivo_abierto = True
                continue

            # 2. Lógica de Marcadores de Trial
            if archivo_abierto and mensaje:
                el_tracker.sendMessage(mensaje)
                print(f"-> MSG a EyeLink: {mensaje}")
                
                if mensaje == "END_EXPERIMENT":
                    print("Cierre ordenado recibido desde Godot.")
                    break
            
        except socket.timeout:
            pass

except KeyboardInterrupt:
    print("\nInterrupción manual.")

finally:
    if archivo_abierto:
        print(f"Deteniendo grabación y rescatando datos en {EDF_FILENAME}...")
        el_tracker.stopRecording()
        time.sleep(0.5)
        
        el_tracker.setOfflineMode()
        time.sleep(0.5)
        
        el_tracker.closeDataFile()
        time.sleep(0.5) # <--- Este respiro es VITAL para que el EyeLink prepare el archivo
        
        ruta_final = os.path.join(carpeta_destino, EDF_FILENAME)
        print(f"Descargando en ruta exacta: {ruta_final}")
        el_tracker.receiveDataFile(EDF_FILENAME, ruta_final)
        print("Archivo guardado con éxito.")
        
    el_tracker.close()
    sock.close()
    print("Servidor de Python cerrado correctamente. Puerto liberado.")