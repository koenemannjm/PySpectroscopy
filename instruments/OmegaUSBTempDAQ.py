from mcculw import ul
from mcculw.enums import TempScale
import time
from datetime import datetime
import os

class OmegaUSBTempLogger:
    def __init__(
        self, 
        board_num=0, 
        channels=None, 
        scale=TempScale.CELSIUS,
        samples_per_cycle=30, 
        sample_interval=0.2,
        wait_time_mins=30, 
        max_time_hrs=12.0,
        file_name="noah_OM_USB_TEMP_meas_T130_09_07_2026.txt",
        dir_output=r"C:\Users\cates\Documents\Cell Pressure Broadening Data\Noah\run2\T130\OM_USB_TEMP_meas\\"
    ):
        self.board_num = board_num
        self.channels = channels if channels is not None else [0, 1, 2, 3, 4, 5, 6, 7]
        self.scale = scale
        self.samples_per_cycle = samples_per_cycle
        self.sample_interval = sample_interval
        
        # Convert units internally
        self.wait_time = int(wait_time_mins * 60)
        self.max_time = max_time_hrs * 3600
        
        # Ensure output directory exists and build path
        os.makedirs(dir_output, exist_ok=True)
        self.file_output = os.path.join(dir_output, file_name)

    def take_samples(self):
        readings = []
        for sample in range(self.samples_per_cycle):
            samp_readings = {}
            t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            samp_readings["timestamp"] = t
            
            for channel in self.channels:
                temp = ul.t_in(self.board_num, channel, self.scale)
                samp_readings[f"ch{channel}"] = temp
                
            readings.append(samp_readings)
            time.sleep(self.sample_interval)

        print_statement = "timestamp           |  CH0  |  CH1  |  CH2  |  CH3  |  CH4  |  CH5  |  CH6  |  CH7  |\n"
        for i in range(self.samples_per_cycle):
            readings_i = readings[i]
            timestamp_i = readings_i["timestamp"]
            T = [readings_i[f"ch{channel}"] for channel in self.channels]
            print_statement += f"{timestamp_i}   {T[0]:.2f}   {T[1]:.2f}   {T[2]:.2f}   {T[3]:.2f}   {T[4]:.2f}   {T[5]:.2f}   {T[6]:.2f}   {T[7]:.2f}\n"
        print(print_statement)
        return readings

    def append_to_file(self, readings, iteration):
        file_exists = os.path.exists(self.file_output)
            
        with open(self.file_output, "a") as f:
            if not file_exists:
                header = ["timestamp", "iteration"] + [f"ch{ch}" for ch in self.channels]
                f.write(",".join(header) + "\n")
                
            for samp_readings in readings:
                values = [samp_readings["timestamp"], f"{iteration:03d}"] + [f'{samp_readings[f"ch{ch}"]:.3f}' for ch in self.channels]
                f.write(",".join(values) + "\n")

    def run(self):
        print(f"""
++++++++++++++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++++++++++++++++++++++++++++++++++++
++++ Starting Temperature Measurement Experiment ++++
++++ Device: OM-USB-TEMP                            ++++
++++ Sample Rate: {1/self.sample_interval:.2f} Hz 
++++ Wait Time: {self.wait_time/60:.1f} mins        
++++ Output File: {self.file_output} 
++++++++++++++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++++++++++++++++++++++++++++++++++++
""")

        counter = 0
        first_iteration = 1
        iteration = 0
        try:
            start_time = time.time()
            run_time = 0.0
            while run_time < self.max_time:

                if not first_iteration:
                    remaining = self.wait_time - counter
                    mins = remaining // 60
                    secs = remaining % 60
                    print(f"Next Sampling in: {mins:02d}:{secs:02d}", end="\r")

                if first_iteration == 1 or counter == self.wait_time:
                    readings = self.take_samples()
                    self.append_to_file(readings, iteration)
                    
                    counter = 0
                    iteration += 1

                first_iteration = 0
                counter += 1
                time.sleep(1)
                current_time = time.time()
                run_time = current_time - start_time

            print("\nExperiment Finished! <3")
                
        except KeyboardInterrupt:
            print("\nExperiment Stopped!")

if __name__ == "__main__":
    logger = OmegaUSBTempLogger()
    logger.run()