import socket
import pylink
import sys
import time
import os

UDP_IP = "127.0.0.1"
PORT_PYTHON = 5005
EYELINK_IP = "100.1.1.1" 
carpeta_destino = "data"

if not os.path.exists(carpeta_destino):
    os.makedirs(carpeta_destino)

# Configurar Socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((UDP_IP, PORT_PYTHON))
sock.settimeout(0.5)

# Conectar al EyeLink
print("Conectando al EyeLink...")
print(f"Conectando al EyeLink en {EYELINK_IP}...")
try:
    el_tracker = pylink.EyeLink(EYELINK_IP)
    print("Conexión hardware establecida con éxito.") # <--- AÑADE ESTO
except RuntimeError as error:
    print(f"Error de conexión con EyeLink: {error}")
    sys.exit()

archivo_abierto = False
EDF_FILENAME = "TEMP.EDF" # Nombre por defecto

try:
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            mensaje = data.decode('utf-8').strip()
            
            # 1. Si llega el ID, abrimos archivo
            if mensaje.startswith("CONNECT:"):
                id_sujeto = mensaje.split(":")[1]
                EDF_FILENAME = f"{id_sujeto}.EDF"
                print(f"Iniciando registro para: {id_sujeto}")
                el_tracker.openDataFile(EDF_FILENAME)
                el_tracker.startRecording(1, 1, 1, 1)
                archivo_abierto = True
                continue

            # 2. Si llega un mensaje y ya estamos grabando
            if archivo_abierto and mensaje:
                el_tracker.sendMessage(mensaje)
                if mensaje == "END_EXPERIMENT":
                    break
            else:
                print(f"DEBUG: Mensaje ignorado (esperando CONNECT): {mensaje}")
                
        except socket.timeout:
            pass
except KeyboardInterrupt:
    pass

finally:
    if archivo_abierto:
        el_tracker.stopRecording()
        time.sleep(0.5)
        el_tracker.setOfflineMode()
        el_tracker.closeDataFile()
        el_tracker.receiveDataFile(EDF_FILENAME, os.path.join(carpeta_destino, EDF_FILENAME))
    el_tracker.close()
    sock.close()