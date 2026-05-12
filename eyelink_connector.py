# eyelink_connector.py
import pylink
import time

class EyeLinkConnector:
    def __init__(self):
        self.tracker = None
        self.connected = False

    def connect(self, ip="100.1.1.1"):  # IP típica del EyeLink
        """Establece conexión con el EyeLink"""
        try:
            self.tracker = pylink.EyeLink(ip)
            self.connected = True
            return True
        except RuntimeError as e:
            print(f"Error conectando al EyeLink: {e}")
            return False

    def calibrate(self):
        """Ejecuta rutina de calibración"""
        if not self.connected:
            return {"success": False, "error": "No conectado"}

        # Configura calibración
        self.tracker.sendCommand("calibration_type = HV9")  # 9 puntos
        self.tracker.doTrackerSetup()  # Abre ventana de calibración
        
        time.sleep(0.5)  # Pequeña pausa para que termine
        return {"success": True}

    def drift_correct(self):
        """Realiza corrección de deriva"""
        if not self.connected:
            return {"success": False, "error": "No conectado"}
        
        # Activa corrección de deriva en el centro
        error = self.tracker.doDriftCorrect(512, 384, 1, 1)  
        return {"success": error == 0}

    def start_recording(self):
        """Inicia grabación EDF"""
        if not self.connected:
            return {"success": False, "error": "No conectado"}
        
        self.tracker.openDataFile("test.edf")
        self.tracker.startRecording(1, 1, 1, 1)
        return {"success": True, "message": "Grabación iniciada"}

    def stop_recording(self):
        """Detiene grabación"""
        if not self.connected:
            return {"success": False, "error": "No conectado"}
        
        self.tracker.stopRecording()
        self.tracker.closeDataFile()
        return {"success": True, "message": "Grabación detenida"}

    def get_gaze_sample(self):
        """Obtiene la muestra de mirada más reciente"""
        if not self.connected:
            return None

        sample = self.tracker.getNewestSample()
        if sample and sample.isRightSample():
            # Datos del ojo derecho (puedes usar left si prefieres)
            gaze = sample.getRightEye().getGaze()
            return {
                "x": gaze[0],
                "y": gaze[1],
                "pupil": sample.getRightEye().getPupilSize(),
                "timestamp": sample.getTime()
            }
        return None

    def close(self):
        """Cierra conexión con el tracker"""
        if self.tracker:
            self.tracker.close()