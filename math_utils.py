import numpy as np

def quaternion_to_euler(quat, sequence='ZXY'):
    """
    Convert quaternion to Euler angles.
    
    Args:
        quat (numpy.ndarray): Quaternion array [w, x, y, z]
        sequence (str): Rotation sequence ('ZXY', 'XYZ'/'RPY', 'YXZ', 'ZYX'/'YPR', 'YZX', 'XZY')
    
    Returns:
        numpy.ndarray: Euler angles [roll, pitch, yaw] in degrees
    """
    # Extract quaternion components
    w, x, y, z = quat
    
    # Precompute common products
    wx = w * x
    wy = w * y
    wz = w * z
    xx = x * x
    xy = x * y
    xz = x * z
    yy = y * y
    yz = y * z
    zz = z * z
    
    # Initialize angles
    roll = pitch = yaw = 0.0
    
    if sequence == "ZXY":  # Aerospace sequence (Z-Y'-X'')
        yaw = np.arctan2(2 * (xy + wz), 1 - 2 * (xx + zz))
        pitch = np.arcsin(2 * (xz - wy))
        roll = np.arctan2(2 * (yz + wx), 1 - 2 * (yy + zz))
        
    elif sequence in ["XYZ", "RPY"]:
        roll = np.arctan2(2 * (yz - wx), 1 - 2 * (xx + yy))
        pitch = np.arcsin(2 * (xz + wy))
        yaw = np.arctan2(2 * (xy - wz), 1 - 2 * (yy + zz))
        
    elif sequence == "YXZ":
        roll = np.arctan2(2 * (xz + wy), 1 - 2 * (xx + yy))
        pitch = -np.arcsin(2 * (yz - wx))
        yaw = np.arctan2(2 * (xy + wz), 1 - 2 * (xx + zz))
        
    elif sequence in ["ZYX", "YPR"]:
        yaw = np.arctan2(2 * (xy + wz), 1 - 2 * (yy + zz))
        pitch = -np.arcsin(2 * (xz - wy))
        roll = np.arctan2(2 * (yz + wx), 1 - 2 * (xx + yy))
        
    elif sequence == "YZX":
        roll = -np.arctan2(2 * (xz - wy), 1 - 2 * (yy + zz))
        pitch = np.arcsin(2 * (xy + wz))
        yaw = -np.arctan2(2 * (yz - wx), 1 - 2 * (xx + zz))
        
    elif sequence == "XZY":
        roll = np.arctan2(2 * (yz + wx), 1 - 2 * (xx + zz))
        pitch = -np.arcsin(2 * (xy - wz))
        yaw = np.arctan2(2 * (xz + wy), 1 - 2 * (yy + zz))
        
    else:
        return np.zeros(3)  # Default or error handling
    
    # Convert to degrees and return as numpy array
    return np.degrees([roll, pitch, yaw])