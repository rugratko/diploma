

# некоторая поверхность отклика
import numpy as np

from scipy.interpolate import griddata

from mpl_toolkits.mplot3d import Axes3D

import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter


def rosenbrock_modified(x, y, z0 = 100.0, k = 0.02):
    return z0 + k*((1-(x-1))**2 + 100*((y-1)-(x-1)**2)**2)


def weight_function(x, y, z0 = 100.0, k = 0.02):
    return z0 + k*(x**2 + y**2)
    

def interpolate_from_calibration(x_mv, y_mv):
    interp_xy = np.hstack((xg_cal.reshape(-1, 1), yg_cal.reshape(-1, 1)))
    return griddata(interp_xy, correction.reshape(-1, 1), (x_mv, y_mv))
    
    
def simulate(xg_test, yg_test, tol):
    pos_err_x = np.random.normal(loc=0.0, scale=tol/2.5, size=(xg_test.shape[0], xg_test.shape[1]))
    pos_err_y = np.random.normal(loc=0.0, scale=tol/2.5, size=(xg_test.shape[0], xg_test.shape[1]))
    x_from_mv = xg_test + pos_err_x
    y_from_mv = yg_test + pos_err_y    
    weight_from_sensor = weight_function(xg_test, yg_test)
    correction_from_mv = interpolate_from_calibration(x_from_mv, y_from_mv)    
    # print(correction_from_mv.shape)
    # plt.hist(correction_from_mv.reshape(-1, 1))
    weight_after_correction = np.divide(weight_from_sensor.reshape(-1, 1), correction_from_mv.reshape(-1, 1))
    # weight_after_correction = weight_from_sensor
    errors = (weight_after_correction - 100.0)/100.0*100.0
    return errors
    
    
def simulate_several_runs(x_test, y_test, tolerance):    
    result_i_th_run =  []
    n_runs = 10
    for i in range(n_runs):
        err = simulate(x_test, y_test, tolerance)
        result_i_th_run.append(err)    
    errors_total = np.array(result_i_th_run).reshape(-1, 1)   
    return errors_total


def get_number_of_bins(sample, d_err):
    return int((np.max(sample)-np.min(sample))/d_err)

fig = plt.figure()

M = 21
xg_cal, yg_cal = np.meshgrid(np.linspace(-8.5, 8.5, M), np.linspace(-8.5, 8.5, M))

correction = weight_function(xg_cal, yg_cal)/100.0
xg_test, yg_test = np.meshgrid(np.linspace(-5.0, 5.0, 50), np.linspace(-5.0, 5.0, 50))
# simulate(xg_test, yg_test, 2.0)

errors_1 = simulate_several_runs(xg_test, yg_test, 2.0)
errors_2 = simulate_several_runs(xg_test, yg_test, 0.1)

band_1 = np.percentile(errors_1, 99.5) - np.percentile(errors_1, 0.5)
band_2 = np.percentile(errors_2, 99.5) - np.percentile(errors_2, 0.5)
print(band_1, band_2)
# print(np.std(errors_1), np.std(errors_2))

# print(np.mean(errors_1), np.mean(errors_2))
# # # # print(errors_total.shape)
d_err = 0.01
plt.hist(errors_1, bins = get_number_of_bins(errors_1, d_err),
          alpha = 0.5, label = 'Допуск = 2 см', density = True)

plt.hist(errors_2, bins = get_number_of_bins(errors_2, d_err), 
          alpha = 0.5, label = 'Допуск = 0.5 см', density = True)

# plt.xlabel('Погрешность после корректировки, %')
# plt.legend()
# # plt.legend()
# # plt.show()
    
        





