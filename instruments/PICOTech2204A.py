import os
import sys
import ctypes
import numpy as np

from picosdk.ps2000 import ps2000
from picosdk.functions import adc2mV

SAMPLES = 5_000
SAMPLE_RATE = 500  # in MS/s
BINS = 32
THRESHOLD = 0

class PicoScope2204A:
    def __init__(self):
        self.status = {}
        self.chandle = ctypes.c_int16()
        self.is_open = False
        self.ch_config = {}

    def connect(self):
        self.status["OpenScope"] = ps2000.ps2000_open_unit()
        if self.status["OpenScope"] <= 0:
            raise RuntimeError(f"ERROR! Failed to Open PicoScope. Error code: {self.status["OpenScope"]}")

        self.chandle = ctypes.c_int16(self.status["OpenScope"])
        self.is_open = True
        print(f"Connected to PicoScope 2204A (Handl: {self.chandle.value})")

    def configure_channels(self, chA_enable, chA_coupling, chA_range, chB_enable, chB_coupling, chB_range):

        if chA_enable != 1 or chA_enable != 0:
            raise ValueError(f"Invalid enable value! 0 = not enabled, 1 = enabled")

        if chA_coupling != 1 or chA_coupling != 0:
            raise ValueError(f"Invalid coupling value! 0 = AC, 1 = DC")

        if chA_range > 10 or chA_range < 1:
            raise ValueError(f"Invalid range value! \n 1=±20mV, 2=±50mV, 3=±100mV, 4=±200mV, 5=±500mV, 6=±1V, 7=±2V, 8=±5V, 9=±10V, 10=±20V")

        if chB_enable != 1 or chB_enable != 0:
            raise ValueError(f"Invalid enable value! 0 = not enabled, 1 = enabled")

        if chB_coupling != 1 or chB_coupling != 0:
            raise ValueError(f"Invalid coupling value! 0 = AC, 1 = DC")

        if chB_range > 10 or chB_range < 1:
            raise ValueError(f"Invalid range value! \n 1=±20mV, 2=±50mV, 3=±100mV, 4=±200mV, 5=±500mV, 6=±1V, 7=±2V, 8=±5V, 9=±10V, 10=±20V")

        if not self.is_open:
            raise RuntimeError("PicoScope was not connected.")


        self.status["setChA"] = ps2000.ps2000_set_channel(self.chandle, 0, chA_enable, chA_coupling, chA_range)
        self.ch_config["ChA_enable"] = chA_enable
        self.ch_config["ChA_coupling"] = chA_coupling
        self.ch_config["ChA_range"] = chA_range

        self.status["setChB"] = ps2000.ps2000_set_channel(self.chandle, 1, chB_enable, chB_coupling, chB_range)
        self.ch_config["ChB_enable"] = chB_enable
        self.ch_config["ChB_coupling"] = chB_coupling
        self.ch_config["ChB_range"] = chB_range

        if self.status["setChA"] == 0 or self.status["setChB"] == 0:
            raise RuntimeError("Failed to apply channel configuration settings to hardware.")

        print("Channel A & B configured.")


    def block_capture(self, num_samples=2_000):

        timebase = 4
        oversample = ctypes.c_int16(1)
        time_interval = ctypes.c_int32()
        time_units = ctypes.c_int32()
        max_samples = ctypes.c_int32()

        check_timebase = ps2000.ps2000_get_timebase(
            self.chandle, timebase, num_samples,
            ctypes.byref(time_interval), ctypes.byref(time_units),
            oversample, ctypes.byref(max_samples)
        )

        if check_timebase == 0:
            raise RuntimeError(f"ERROR! Failed to get timebase!")

        ps2000.ps2000_run_block(self.chandle, num_samples, timebase, oversample, ctypes.byref(ctypes.c_int32(0)))

        ready = ctypes.c_int16(0)
        while ready.value == 0:
            ready = ctypes.c_int16(ps2000.ps2000_ready(self.chandle))

        buffer_a = (ctypes.c_int16 * num_samples)()
        buffer_b = (ctypes.c_int16 * num_samples)()
        overflow = ctypes.c_int16()

        ps2000.ps2000_get_values(
            self.chandle, ctypes.byref(buffer_a), ctypes.byref(buffer_b),
            None, None, ctypes.byref(overflow), num_samples
        )

        max_adc = 32767
        chA_mv = adc2mV(buffer_a, self.ch_config["ChA_range"], max_adc)
        chB_mv = adc2mV(buffer_b, self.ch_config["ChB_range"], max_adc)

        time_ms = np.linspace(0, (num_samples * time_interval.value) / 1_000_000.0, num_samples)

        return time_ms, np.array(chA_mv), np.array(chB_mv)

    def disconnect(self):
        if self.is_open:
            ps2000.ps2000_close_unit(self.chandle)
            self.is_open = False
            print("PicoScope disconnected successfully.")