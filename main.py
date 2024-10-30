import sys
import xsensdeviceapi as xda
from device_manager import DeviceManager
from callback_handler import XdaCallback
from math_utils import quaternion_to_euler

def main():
    print("Creating XsControl object...")
    manager = DeviceManager()

    try:
        print("Scanning for devices...")
        manager.scan_and_connect()
        
        callback = XdaCallback()
        manager.device.addCallbackHandler(callback)

        print("Configuring the device...")
        manager.configure_device()

        print("Creating a log file...")
        manager.setup_logging()

        print("Putting device into measurement mode...")
        manager.start_measurement()

        print("Starting recording...")
        manager.start_recording()

        print("Main loop. Recording data for 100 seconds.")
        startTime = xda.XsTimeStamp_nowMs()
        while xda.XsTimeStamp_nowMs() - startTime <= 100000:
            if callback.packetAvailable():
                packet = callback.getNextPacket()
                process_packet(packet)

        print("\nStopping recording...")
        manager.stop_recording()

        print("Closing log file...")
        manager.close_logging()

        print("Removing callback handler...")
        manager.device.removeCallbackHandler(callback)

        print("Disconnecting...")
        manager.disconnect()

    except RuntimeError as error:
        print(error)
        sys.exit(1)
    # except:
    #     print("An unknown fatal error has occurred. Aborting.")
    #     sys.exit(1)
    else:
        print("Successful exit.")

def process_packet(packet):
    s = ""
    if packet.containsCalibratedData():
        acc = packet.calibratedAcceleration()
        s = "Acc X: %.2f" % acc[0] + ", Acc Y: %.2f" % acc[1] + ", Acc Z: %.2f" % acc[2]
        gyr = packet.calibratedGyroscopeData()
        s += " |Gyr X: %.2f" % gyr[0] + ", Gyr Y: %.2f" % gyr[1] + ", Gyr Z: %.2f" % gyr[2]
        mag = packet.calibratedMagneticField()
        s += " |Mag X: %.2f" % mag[0] + ", Mag Y: %.2f" % mag[1] + ", Mag Z: %.2f" % mag[2]

    if packet.containsOrientation():
        quaternion = packet.orientationQuaternion()
        s = "q0: %.2f" % quaternion[0] + ", q1: %.2f" % quaternion[1] + ", q2: %.2f" % quaternion[2] + ", q3: %.2f " % quaternion[3]
        euler = packet.orientationEuler()
        s += " |Roll: %.2f" % euler.x() + ", Pitch: %.2f" % euler.y() + ", Yaw: %.2f " % euler.z()
        calculated_euler = quaternion_to_euler(quaternion, "ZYX")
        s += " |calculated Roll: %.2f" % calculated_euler[0] + ", Pitch: %.2f" % calculated_euler[1] + ", Yaw: %.2f " % calculated_euler[2]
    
    if packet.containsLatitudeLongitude():
        latlon = packet.latitudeLongitude()
        s += " |Lat: %7.2f" % latlon[0] + ", Lon: %7.2f " % latlon[1]

    if packet.containsAltitude():
        s += " |Alt: %7.2f " % packet.altitude()

    if packet.containsVelocity():
        vel = packet.velocity(xda.XDI_CoordSysEnu)
        s += " |E: %7.2f" % vel[0] + ", N: %7.2f" % vel[1] + ", U: %7.2f " % vel[2]

    print("%s\r" % s, end="", flush=True)

if __name__ == '__main__':
    main()