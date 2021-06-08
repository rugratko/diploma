import numpy as np

def get_actual_points(x_meas, y_meas):
    x_snap, y_snap = np.meshgrid(np.linspace(-60, 60, 15),
                                 np.linspace(-60, 60, 15))

    x_snap = x_snap.reshape(-1, 1)
    y_snap = y_snap.reshape(-1, 1)

    dist = np.sqrt((x_snap-x_meas)**2+(y_snap-y_meas)**2)

    i_snap = np.argmin(dist)

    return x_snap[i_snap], y_snap[i_snap]

result = get_actual_points(56.5135, -4.5325)
print(result[0][0], result[1][0])