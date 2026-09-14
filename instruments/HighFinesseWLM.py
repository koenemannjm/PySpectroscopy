import os
from pylablib.devices import HighFinesse

APP_FOLDER = r"C:\Program Files (x86)\HighFinesse\Wavelength Meter WS6 3312"
DLL_PATH = os.path.join(APP_FOLDER, "Projects", "64")
APP_PATH = os.path.join(APP_FOLDER, "wlm_ws6.exe")

class HighFinesseWLM:
    def __init__(
        self,
        serial_number=3312
    ):
        self.serial_number = serial_number
        self.wlm = None

    def connect(self):
        print("Connecting to WLM...")
        self.wlm = HighFinesse.WLM(
            self.serial_number, 
            dll_path=DLL_PATH, 
            app_path=APP_PATH
        )

    def configManualExpos(self, time):
        # TIME IS IN UNITS OF ms
        if self.wlm is None:
            self.connect()

        time *= 1e-3

        self.wlm.set_exposure_mode("manual")
        self.wlm.set_exposure(time, sensor="all")

    def read_frequency(self):
        if self.wlm is None:
            self.connect()
        
        f = float(self.wlm.get_frequency())
        return f

    def read_wavelength(self):
        if self.wlm is None:
            self.connect()
        
        wavl = float(self.wlm.get_wavelength())
        return wavl

    def close(self):
        if self.wlm is not None:
            self.wlm.close()
            self.wlm = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

def main():
    # Using context manager for safe connection handling
    with HighFinesseWLM() as wlm:
        wlm.connect()
        wlm.configManualExpos(15)
        wavl = wlm.read_wavelength()
        f = wlm.read_frequency()
        print(f"Frequency: {f}, Wavelength: {wavl}")
        wlm.close()

if __name__ == "__main__":
    main()