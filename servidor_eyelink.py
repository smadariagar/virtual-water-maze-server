import socket
import pylink
import threading

# Configuración
UDP_IP = "127.0.0.1"
PORT_PYTHON = 5005
PORT_GODOT = 5006

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, PORT_PYTHON))

class GodotCalDisplay(pylink.EyeLinkCustomDisplay):
    def draw_cal_target(self, x, y):
        # Envía las coordenadas del punto a Godot
        msg = f"CAL_DRAW,{int(x)},{int(y)}"
        sock.sendto(msg.encode(), (UDP_IP, PORT_GODOT))

    def clear_cal_display(self):
        sock.sendto(b"CAL_ERASE", (UDP_IP, PORT_GODOT))

# Inicialización
el_tracker = pylink.EyeLink(None) # Usa None para modo Dummy
pylink.openGraphicsEx(GodotCalDisplay())

def escuchar_godot():
    while True:
        data, addr = sock.recvfrom(1024)
        msg = data.decode()
        if msg == "CALIBRATE":
            el_tracker.doTrackerSetup()
            sock.sendto(b"CAL_END", (UDP_IP, PORT_GODOT))
        # Aquí puedes añadir más lógica para eventos de trial
        print(f"Comando recibido: {msg}")

# Hilo en segundo plano
thread = threading.Thread(target=escuchar_godot, daemon=True)
thread.start()

print("Servidor listo. Esperando comandos...")
input("Presiona Enter para cerrar.\n")