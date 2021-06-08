import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import LinearLocator, FormatStrFormatter
from matplotlib import cm


def weight_function(x, y, z0 = 100.0, k = 0.02):
    """Функция для генерации отклонения веса при эксцентриситете груза

    Args:
        x (float): параметр x
        y (float): параметр y
        z0 (float, optional): высота. Defaults to 100.0.
        k (float, optional): коэффициент искривления. Defaults to 0.02.

    Returns:
        float: уравнение параболы
    """    
    return z0 + k*(x**2 + y**2)
    

def interpolate_from_calibration(x_mv, y_mv):
    interp_xy = np.hstack((xg_cal.reshape(-1, 1), yg_cal.reshape(-1, 1)))
    return griddata(interp_xy, correction.reshape(-1, 1), (x_mv, y_mv))
    
    
def simulate(xg_test, yg_test, tol):    
    """Симуляция установки груза на платформу 
    с погрешностью распознавания

    Args:
        xg_test (float): положение груза по x
        yg_test (float): положение груза по y
        tol (float): погрешность распознавания положения

    Returns:
        float: массив погрешности измерения после 
        корректировки для одного набора тестовых точек
    """    
    # генерация погрешности положения по x и y
    pos_err_x = np.random.normal(loc=0.0, scale=tol/2.5, 
                                 size=(xg_test.shape[0], xg_test.shape[1]))
    pos_err_y = np.random.normal(loc=0.0, scale=tol/2.5, 
                                 size=(yg_test.shape[0], yg_test.shape[1]))
    # задание положения с погрешностью по x и y
    x_from_mv = xg_test + pos_err_x
    y_from_mv = yg_test + pos_err_y   
    # получение веса с искажением от датчика
    weight_from_sensor = weight_function(xg_test, yg_test)
    # получение корректировки к весу согласно результату с камеры
    correction_from_mv = interpolate_from_calibration(x_from_mv, y_from_mv)
    # применение корректировки к весу
    weight_after_correction = np.divide(weight_from_sensor.reshape(-1, 1), 
                                        correction_from_mv.reshape(-1, 1))
    # перевод в проценты
    errors = (weight_after_correction - 100.0)/100.0*100.0
    return errors
    
    
def simulate_several_runs(x_test, y_test, tolerance):    
    """Симуляция череды испытаний

    Args:
        x_test (float): массив по x
        y_test (float): массив по y
        tolerance (float): допустимая погрешность

    Returns:
        np_array: массив погрешностей
    """    
    result_i_th_run =  []
    n_runs = 10 #число попыток
    for i in range(n_runs):
        err = simulate(x_test, y_test, tolerance) #запуск симуляции
        result_i_th_run.append(err)    
    errors_total = np.array(result_i_th_run).reshape(-1, 1)   
    return errors_total


def get_number_of_bins(sample, d_err):
    """Подсчет столбцов для гистограммы

    Args:
        sample (np_array): массив погрешностей
        d_err (float): коэффициент числа столбцов

    Returns:
        int: число столбцов
    """    
    return int((np.max(sample)-np.min(sample))/d_err)


cal_mesh_size = 10 #густота сетки калибровки
test_mesh_size = 50 #густота сетки испытаний
xg_cal, yg_cal = np.meshgrid(np.linspace(-8.5, 8.5, cal_mesh_size), 
                             np.linspace(-8.5, 8.5, cal_mesh_size)) #задание сетки для калибровки
xg_test, yg_test = np.meshgrid(np.linspace(-5.0, 5.0, test_mesh_size), 
                               np.linspace(-5.0, 5.0, test_mesh_size)) #задание сетки для испытаний

correction = weight_function(xg_cal, yg_cal)/100.0 #функция искривления веса (ось Z)

fig = plt.figure() #создание бланка графика
ax = fig.gca(projection='3d') #задание типа графика
surf = ax.plot_surface(xg_cal, yg_cal, correction, cmap=cm.coolwarm,
                       linewidth=0, antialiased=False) #ввод переменных в график

# Настраиваем ось Z
ax.set_zlim(0.95, 1.05)
ax.zaxis.set_major_locator(LinearLocator(10)) 
ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))
fig.colorbar(surf, shrink=0.5, aspect=5) # Добавление цветового индикатора
plt.show() #Запуск графика с искривлением веса

errors_1 = simulate_several_runs(xg_test, yg_test, 2.0) #прогон эмулятором взвешиваний с погрешностью положения 1 см
errors_2 = simulate_several_runs(xg_test, yg_test, 0.5) #прогон эмулятором взвешиваний с погрешностью положения 0.25 см

# высчитываем процентиль
band_1 = np.percentile(errors_1, 99.5) - np.percentile(errors_1, 0.5) 
band_2 = np.percentile(errors_2, 99.5) - np.percentile(errors_2, 0.5)

# вывод результатов 
print(band_1, band_2) #доверительный интервал 
print(np.std(errors_1), np.std(errors_2)) #среднеквадратичное отклонение
print(np.mean(errors_1), np.mean(errors_2)) #среднее арифметическое

d_err = 0.005 #коэффициент количества столбцов

# задание параметров гистограммы и ее вывод
plt.hist(errors_1, bins = get_number_of_bins(errors_1, d_err),
          alpha = 0.5, label = 'Допуск = 1 см', density = True)
plt.hist(errors_2, bins = get_number_of_bins(errors_2, d_err), 
          alpha = 0.5, label = 'Допуск = 0.1 см', density = True)
plt.xlabel('Погрешность после корректировки, %')
plt.ylabel('Плотность вероятности rho(x)')
plt.legend()
plt.show()
    
        





