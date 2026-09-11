import os
from pylablib.devices import HighFinesse

class HighFinesseWLM:
    def __init__(
        self,
        serial_number=3312,
        app_folder=r"C:\Program Files (x86)\HighFinesse\Wavelength Meter WS6 3312"
    ):
        self.serial_number = serial_number
        self.app_folder = app_folder
        self.dll_path = os.path.join(app_folder, "Projects", "64")
        self.app_path = os.path.join(app_folder, "wlm_ws6.exe")
        self.wlm = None

    def connect(self):
        print("Connecting to WLM...")
        self.wlm = HighFinesse.WLM(
            self.serial_number, 
            dll_path=self.dll_path, 
            app_path=self.app_path
        )

    def read(self):
        if self.wlm is None:
            self.connect()
        
        f = float(self.wlm.get_frequency())
        wavl = float(self.wlm.get_wavelength())
        return f, wavl

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
        f, wavl = wlm.read()
        print(f"Frequency: {f}, Wavelength: {wavl}")

if __name__ == "__main__":
    main()