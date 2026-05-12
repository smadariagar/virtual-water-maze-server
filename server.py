# server.py
import socket
import json
import threading
import time
from eyelink_connector import EyeLinkConnector

class EyeLinkServer:
    def __init__(self, host="127.0.0.1", port=5555):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(1)  # Solo un cliente (Godot)
        self.conn = None
        self.running = False
        self.el = EyeLinkConnector()

    def send_json(self, data):
        """Envía datos formateados como JSON con salto de línea"""
        if self.conn:
            try:
                message = json.dumps(data) + "\n"
                self.conn.send(message.encode())
            except:
                print("Error enviando datos al cliente")

    def handle_command(self, command):
        """Procesa comandos recibidos de Godot"""
        try:
            action = command.get("action")
            
            if action == "CALIBRATE":
                result = self.el.calibrate()
                self.send_json({"type": "STATUS", "data": result})

            elif action == "DRIFT_CORRECT":
                result = self.el.drift_correct()
                self.send_json({"type": "STATUS", "data": result})

            elif action == "START_RECORDING":
                result = self.el.start_recording()
                self.send_json({"type": "STATUS", "data": result})

            elif action == "STOP_RECORDING":
                result = self.el.stop_recording()
                self.send_json({"type": "STATUS", "data": result})

            elif action == "CONNECT_EYELINK":
                ip = command.get("ip", "100.1.1.1")
                result = self.el.connect(ip)
                self.send_json({"type": "STATUS", "data": {"connected": result}})

        except Exception as e:
            self.send_json({"type": "STATUS", "data": {"error": str(e)}})

    def stream_gaze(self):
        """Hilo que envía muestras de mirada continuamente (opcional)"""
        while self.running:
            sample = self.el.get_gaze_sample()
            if sample:
                self.send_json({
                    "type": "GAZE",
                    "timestamp": sample["timestamp"],
                    "data": sample
                })
            time.sleep(0.002)  # ~500Hz (ajustable)

    def start(self):
        """Inicia el servidor"""
        print(f"Servidor EyeLink esperando conexión en {self.host}:{self.port}")
        self.conn, addr = self.server.accept()
        print(f"Godot conectado desde {addr}")
        self.running = True

        # Hilo para enviar datos de mirada
        # Descomentar si necesitas streaming automático
        # threading.Thread(target=self.stream_gaze, daemon=True).start()

        buffer = ""
        while self.running:
            try:
                data = self.conn.recv(4096).decode()
                if not data:
                    break

                buffer += data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    command = json.loads(line)
                    self.handle_command(command)

            except Exception as e:
                print(f"Error: {e}")
                break

        self.close()

    def close(self):
        """Limpia recursos"""
        self.running = False
        self.el.close()
        if self.conn:
            self.conn.close()
        self.server.close()

if __name__ == "__main__":
    server = EyeLinkServer()
    try:
        server.start()
    except KeyboardInterrupt:
        server.close()