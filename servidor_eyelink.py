import socket
import pylink
import sys

# 1. Configurar la conexión UDP local
UDP_IP = "127.0.0.1" # localhost
UDP_PORT = 5005      # Puerto de comunicación
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

# 2. Iniciar conexión con EyeLink (Usaremos 'None' para modo Dummy si no está conectado)
try:
    el_tracker = pylink.EyeLink(None) # Cambia 'None' por la IP del EyeLink cuando esté conectado
    print("Conectado al EyeLink.")
    
    # Abrir un archivo temporal de datos
    el_tracker.openDataFile("test.edf")
    el_tracker.startRecording(1, 1, 1, 1)
except Exception as e:
    print(f"Error conectando a EyeLink: {e}")
    sys.exit()

print(f"Servidor Python escuchando en el puerto {UDP_PORT}...")
print("Esperando mensajes de Godot...")

try:
    while True:
        # 3. Escuchar mensajes de Godot (se queda pausado aquí hasta recibir algo)
        data, addr = sock.recvfrom(1024) # buffer de 1024 bytes
        mensaje = data.decode('utf-8')
        
        print(f"-> Recibido desde Godot: {mensaje}")

        # 4. Lógica de comunicación con EyeLink
        if mensaje == "CALIBRATE":
            print("   Instruyendo al EyeLink para calibrar...")
            # En modo real, esto abre la pantalla de calibración
            el_tracker.doTrackerSetup() 
        else:
            # Si es cualquier otro mensaje, lo inyecta como un MSG en el archivo .edf
            el_tracker.sendMessage(mensaje)
            print(f"   Marcador '{mensaje}' guardado en el archivo del EyeLink.")

except KeyboardInterrupt:
    print("\nCerrando servidor y guardando datos...")
    el_tracker.stopRecording()
    el_tracker.closeDataFile()
    el_tracker.close()