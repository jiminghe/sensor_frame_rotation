import sys
import xsensdeviceapi as xda
from device_manager import DeviceManager
from callback_handler import XdaCallback
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import time
import numpy as np
from math_utils import quaternion_to_euler

app = Flask(__name__)
socketio = SocketIO(app)


def normalize_quaternion(q):
    norm = np.linalg.norm(q)
    return q / norm

def reorder_quaternion_for_threejs(q0, q1, q2, q3):
    # [q0, q1, q2, q3] -> [w, x, y, z] for ENU to Three.js conversion needs:
    return [q0, q2, q3, q1]  # Reorder for Three.js

def packet_processing_thread(manager, callback):
    while True:
        if callback.packetAvailable():
            packet = callback.getNextPacket()
            if packet.containsOrientation():
                quaternion = packet.orientationQuaternion()
                quaternion = normalize_quaternion(quaternion)
                reversed_quat = np.array([quaternion[0], -quaternion[1], -quaternion[2], -quaternion[3]])
                reversed_quat = normalize_quaternion(reversed_quat)
                
                reordered_quaternion = reorder_quaternion_for_threejs(quaternion[0], quaternion[1], quaternion[2], quaternion[3])
                reordered_reversed_quaternion = reorder_quaternion_for_threejs(reversed_quat[0], reversed_quat[1], reversed_quat[2], reversed_quat[3])
                
                euler_original = quaternion_to_euler(quaternion, "ZYX")
                euler_reversed = quaternion_to_euler(reversed_quat, "ZYX")
                
                data = {
                    "original": {
                        "q0": reordered_quaternion[0],
                        "q1": reordered_quaternion[1],
                        "q2": reordered_quaternion[2],
                        "q3": reordered_quaternion[3],
                        "euler": {
                            "roll": euler_original[0],
                            "pitch": euler_original[1],
                            "yaw": euler_original[2]
                        }
                    },
                    "reversed": {
                        "q0": reordered_reversed_quaternion[0],
                        "q1": reordered_reversed_quaternion[1],
                        "q2": reordered_reversed_quaternion[2],
                        "q3": reordered_reversed_quaternion[3],
                        "euler": {
                            "roll": euler_reversed[0],
                            "pitch": euler_reversed[1],
                            "yaw": euler_reversed[2]
                        }
                    }
                }
                socketio.emit('quaternion_data', data)
        time.sleep(0.01)

@app.route('/')
def index():
    return render_template('index.html')

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

        print("Putting device into measurement mode...")
        manager.start_measurement()

        print("Starting recording...")
        manager.start_recording()

        # Start a packet processing thread
        thread = threading.Thread(target=packet_processing_thread, args=(manager, callback))
        thread.daemon = True
        thread.start()

        print("Starting Flask app...")
        socketio.run(app, host='0.0.0.0', port=5000)

    except RuntimeError as error:
        print(error)
        sys.exit(1)
    except:
        print("An unknown fatal error has occurred. Aborting.")
        sys.exit(1)

if __name__ == '__main__':
    main()