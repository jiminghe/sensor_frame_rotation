import xsensdeviceapi as xda
from callback_handler import XdaCallback

class DeviceManager:
    def __init__(self):
        self.control = xda.XsControl_construct()
        assert self.control is not None
        self.device = None

    def scan_and_connect(self):
        portInfoArray = xda.XsScanner_scanPorts()
        mtPort = xda.XsPortInfo()

        for i in range(portInfoArray.size()):
            if portInfoArray[i].deviceId().isMti() or portInfoArray[i].deviceId().isMtig():
                mtPort = portInfoArray[i]
                break

        if mtPort.empty():
            raise RuntimeError("No MTi device found. Aborting.")

        if not self.control.openPort(mtPort.portName(), mtPort.baudrate()):
            raise RuntimeError("Could not open port. Aborting.")

        self.device = self.control.device(mtPort.deviceId())
        assert self.device is not None

    def configure_device(self):
        if not self.device.gotoConfig():
            raise RuntimeError("Could not put device into configuration mode. Aborting.")

        configArray = xda.XsOutputConfigurationArray()
        configArray.push_back(xda.XsOutputConfiguration(xda.XDI_PacketCounter, 0))
        configArray.push_back(xda.XsOutputConfiguration(xda.XDI_SampleTimeFine, 0))

        if self.device.deviceId().isImu():
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_Acceleration, 100))
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_RateOfTurn, 100))
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_MagneticField, 100))
        elif self.device.deviceId().isVru() or self.device.deviceId().isAhrs():
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_Quaternion, 100))
        elif self.device.deviceId().isGnss():
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_Quaternion, 100))
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_LatLon, 100))
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_AltitudeEllipsoid, 100))
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_VelocityXYZ, 100))
        else:
            raise RuntimeError("Unknown device while configuring. Aborting.")

        if not self.device.setOutputConfiguration(configArray):
            raise RuntimeError("Could not configure the device. Aborting.")

    def setup_logging(self, logFileName="logfile.mtb"):
        if self.device.createLogFile(logFileName) != xda.XRV_OK:
            raise RuntimeError("Failed to create a log file. Aborting.")

    def start_measurement(self):
        if not self.device.gotoMeasurement():
            raise RuntimeError("Could not put device into measurement mode. Aborting.")

    def start_recording(self):
        if not self.device.startRecording():
            raise RuntimeError("Failed to start recording. Aborting.")

    def stop_recording(self):
        if not self.device.stopRecording():
            raise RuntimeError("Failed to stop recording. Aborting.")

    def close_logging(self):
        if not self.device.closeLogFile():
            raise RuntimeError("Failed to close log file. Aborting.")

    def disconnect(self):
        self.control.close()