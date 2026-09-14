from time import sleep
from toptica.lasersdk.client import Client, DeviceNotFoundError, SerialConnection
import serial


class TopticaDLCPro:

    def __init__(self, port="COM4"):
        self.port = port
        self.laser = None

        # DLC Pro variables
        self.set_temp = "laser1:dl:tc:temp-set"
        self.set_current = "laser1:dl:cc:current-set"
        self.set_voltage = "laser1:dl:pc:voltage-set"
        self.set_grating = "laser1:dl:grating:goto-pos"

        self.move_rel_grating = "laser1:dl:grating:move-rel"

        self.get_temp = "laser1:dl:tc:temp-act"
        self.get_current = "laser1:dl:cc:current-act"
        self.get_voltage = "laser1:dl:pc:voltage-act"
        self.get_grating = "laser1:dl:grating:pos-act"

    def connect(self):
        print(f"Connecting to Laser on {self.port}...")
        try:
            self.laser = Client(SerialConnection(self.port))
            self.laser.open()
        except DeviceNotFoundError as e:
            print(
                f"Error: Could not find Toptica DLC Pro controller on port"
                f" '{self.port}'. Check USB/serial connections."
            )
            raise e

    def close(self):
        if self.laser:
            self.laser.close()
            self.laser = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def set_laser_temperature(self, temp):
        self.laser.set(self.set_temp, temp)

    def set_laser_current(self, current):
        self.laser.set(self.set_current, current)

    def set_laser_voltage(self,voltage):
        self.laser.set(self.set_voltage, voltage)

    def get_laser_temperature(self):
        self.laser.get(self.get_temp)

    def get_laser_current(self):
        self.laser.get(self.get_current)

    def get_laser_voltage(self):
        self.laser.get(self.get_voltage)

    def get_laser_grating(self):
        self.laser.get(self.get_grating)


class TopticaMotorController:

    def __init__(
            self,
            port="COM4",
            baudrate=9600,
            timeout=10.0
    ):
        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=timeout
        )
        sleep(0.5)

        # TERMINATION CHAR 0xA = '\n' = LF

        #

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def send_command(self, cmd: str) -> str:
        full_cmd = f"{cmd}\r\n"
        self.ser.write(full_cmd.encode("ascii"))
        sleep(0.1)
        response = self.ser.read_all().decode("ascii", errors="ignore").strip()
        return response

    def get_position(self):
        res = self.send_command("(param-ref 'pos)")
        return res

    def move_to(self, target_steps):
        res = self.send_command(f"pos={target_steps}")
        return res

    def disconnect(self):
        if self.ser.is_open:
            self.ser.close()


def main():

    with TopticaDLCPro(port="COM7") as dlc:

        print(dlc.get_laser_voltage())


    with TopticaMotorController(port="COM5") as mc:

        pos = mc.get_position()

        print(f"Response: {pos!r}")

if __name__ == "__main__":
    main()