import os
import time
import logging
import sys
import clr
import matplotlib.pyplot as plt
from scipy import signal
import numpy as np
from ctypes import *
from System import Decimal

sys.path.append(r"C:\\Program Files\\Thorlabs\\Kinesis")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.FilterFlipperCLI.dll")
clr.AddReference("System.Collections")
clr.AddReference("System.Linq")

from Thorlabs.MotionControl.DeviceManagerCLI import DeviceManagerCLI 
from Thorlabs.MotionControl.DeviceManagerCLI import DeviceNotReadyException 
from Thorlabs.MotionControl.FilterFlipperCLI import FilterFlipper

class MFF101FlipperMirror:
    def __init__(self,deviceID):
        self.device = self.SetupDevice(deviceID)
    
    def SetupDevice(self,deviceID):
        DeviceManagerCLI.BuildDeviceList()
        device = FilterFlipper.CreateFilterFlipper(str(deviceID))
        device.Connect(deviceID)
        device.StartPolling(1)
        time.sleep(0.25)
        device.EnableDevice()
        time.sleep(0.25)
        return device

    def SetMode(self,mode):
        if mode == 'on':
            self.device.SetPosition(2,60000)
        elif mode == 'off':
            self.device.SetPosition(1,60000)
        else:
            print('wrong mode, try again')
        return
    
    def HomeMirror(self):
        self.device.Home(60000)
        return
