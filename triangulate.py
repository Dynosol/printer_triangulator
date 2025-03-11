import numpy as np

def rssi_to_distance(rssi, tx_power=-50, n=2.0):
    # tx_power = RSSI at 1 meter (printer-specific; estimate or calibrate)
    return 10 ** ((tx_power - rssi) / (10 * n))  # Distance in meters

def trilaterate(points, distances):
    # Solve using least squares (example pseudocode)
    # Points = [(x1, y1), (x2, y2), ...], distances = [d1, d2, ...]
    # Returns estimated (x, y)
    A = []
    b = []
    for (x, y), d in zip(points, distances):
        A.append([2*x, 2*y])
        b.append(d**2 - x**2 - y**2)
    A = np.array(A)
    b = np.array(b)
    return np.linalg.lstsq(A, b, rcond=None)[0]