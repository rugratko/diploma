alpha = 0.07989613
beta = 0.0010399711 * 20
gamma = 0.0038807219 * 20
gravity = 9.81
k_amp = 200
k_adc = 65536/5
U_s = 5


def get_sensor_weight(weight, x, y):
    weight_z = weight/1000 * alpha * gravity
    weight_x = weight/1000 * beta * x/1000 * gravity
    weight_y = weight/1000 * gamma * y/1000 * gravity
    return k_amp*k_adc*U_s*(weight_z+weight_x+weight_y)
