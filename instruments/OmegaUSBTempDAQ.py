from mcculw import ul
from mcculw.enums import TempScale
import time
from datetime import datetime
import os

class OmegaUSBTempLogger:
    def __init__(
        self, 
        board_num=0
    ):
        self.board_num = board_num
        self.channels = [0, 1, 2, 3, 4, 5, 6, 7]
        self.scale = TempScale.CELSIUS

    def sample_all_channels(self):
        
        samp_readings = {}
        t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        samp_readings["timestamp"] = t
        
        for channel in self.channels:
            temp = ul.t_in(self.board_num, channel, self.scale)
            samp_readings[f"ch{channel}"] = temp

        return samp_readings

    def sample_single_channel(self, channel):

        if channel not in self.channels:
            raise ValueError(f"Invalid channel value: {channel}! select from {self.channels}")

        samp_reading = {}
        t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        samp_reading["timestamp"] = t

        temp = ul.t_in(self.board_num, channel, self.scale)
        samp_reading[f"ch{channel}"] = temp

        return samp_reading
