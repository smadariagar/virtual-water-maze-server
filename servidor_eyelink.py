import socket
import pylink
import sys

# Configuración
UDP_IP = "127.0.0.1"
PORT_PYTHON = 5005
PORT_GODOT = 5006

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, PORT_PYTHON))

class GodotCalDisplay(pylink.EyeLinkCustomDisplay):
    def __init__(self):
        super().__init__()

    # --- Funciones obligatorias del SDK ---
    def setup_cal_display(self):
        sock.sendto(b"CAL_START", (UDP_IP, PORT_GODOT))

    def exit_cal_display(self):
        sock.sendto(b"CAL_END", (UDP_IP, PORT_GODOT))

    def clear_cal_display(self):
        sock.sendto(b"CAL_ERASE", (UDP_IP, PORT_GODOT))

    def draw_cal_target(self, x, y):
        msg = f"CAL_DRAW,{int(x)},{int(y)}"
        sock.sendto(msg.encode(), (UDP_IP, PORT_GODOT))

    def erase_cal_target(self):
        sock.sendto(b"CAL_ERASE", (UDP_IP, PORT_GODOT))

    def get_input_key(self):
        # Intentamos leer si Godot nos envió una tecla
        sock.setblocking(False) # No congelar
        try:
            data, addr = sock.recvfrom(1024)
            msg = data.decode()
            if msg == "ACCEPT_CAL":
                return [pylink.KeyInput(32, 0)] # Espacio
            elif msg == "ESC_CAL":
                return [pylink.KeyInput(27, 0)] # ESC
        except:
            pass
        sock.setblocking(True)
        return None

# --- Ejecución ---
el_tracker = pylink.EyeLink(None) # Usa None para modo Dummy
pylink.openGraphicsEx(GodotCalDisplay())

el_tracker.openDataFile("test.edf")
el_tracker.startRecording(1, 1, 1, 1)

print("Servidor Python listo...")

# Aquí recibimos el comando para CALIBRAR
while True:
    data, addr = sock.recvfrom(1024)
    if data.decode() == "CALIBRATE":
        print("Iniciando calibración...")
        el_tracker.doTrackerSetup()
        print("Calibración terminada.")