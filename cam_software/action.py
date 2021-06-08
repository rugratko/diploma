import statistics, time, json
from pos_detector import connect_to_camera, connect_to_camera_wo_reboot
from weight_sensor import get_sensor_weight
from calculation import get_weight_scaling

calibration_points = {'p1': [0, 0],
                      'p2': [0, -40],
                      'p3': [0, 40],
                      'p4': [-40, 0],
                      'p5': [40, 0]}


def calibrating_mode(message_chat, shots, step, n_steps, weight):
    message_chat.appendPlainText(f'\nЭтап калибровки {step+1}/{n_steps}\n')
    time.sleep(1)
    stage_data = connect_to_camera_wo_reboot(shots)
    x_step, y_step = get_mean_rect_position(stage_data)
    scaled_value = get_sensor_weight(weight, x_step, y_step)
    stage_data['relative_rect_pos_mean'] = [x_step, y_step]
    stage_data['scaled_value'] = scaled_value
    stage_data['weight'] = weight
    stage_data['coeffs'] = [0, 0, 0]
    message_chat.appendPlainText(f'''Промежуточные данные:
    Положение по X: {x_step} мм;
    Положение по Y: {y_step} мм;
    Показания весов: {scaled_value};''')
    time.sleep(1)
    return stage_data


def scaling_mode(message_chat, shots, preset):
    time.sleep(1)
    stage_data = connect_to_camera_wo_reboot(shots)
    x_step, y_step = get_mean_rect_position(stage_data)
    weight = get_sensor_weight(1500, x_step, y_step)
    time.sleep(1)
    with open('accuracy_presets/' + preset, "r") as read_file:
        data = json.load(read_file)
    alpha, beta, gamma = data['Result']
    scaled_weight = get_weight_scaling(weight, alpha, beta, gamma, x_step, y_step)
    scaled_corr = scaled_weight[0]
    scaled_wo_corr = scaled_weight[1]
    message_chat.appendPlainText(f'''Результат взвешивания:
    Положение по X: {x_step} мм;
    Положение по Y: {y_step} мм;
    Показания весов без коррекции: {scaled_wo_corr * 1000} г;
    Показания весов с коррекцией: {scaled_corr * 1000} г;''')


def calibrating_mode_simple(message_chat, shots, step, n_steps, weight):
    message_chat.appendPlainText(f'\n[SIMPLE] Этап калибровки {step+1}/{n_steps}\n')
    time.sleep(1)
    stage_data = connect_to_camera_wo_reboot(shots)
    x_step, y_step = get_mean_rect_position(stage_data)
    scaled_value = get_sensor_weight(weight, x_step, y_step)
    stage_data['relative_rect_pos_mean'] = [x_step, y_step]
    stage_data['scaled_value'] = scaled_value
    stage_data['weight'] = weight
    message_chat.appendPlainText(f'''Промежуточные данные:
    Положение по X: {x_step} мм;
    Положение по Y: {y_step} мм;
    Показания весов: {scaled_value};''')
    time.sleep(1)
    return stage_data


def get_mean_rect_position(params_dict):
    x_set = []
    y_set = []
    for step in params_dict:
        x_set.append(params_dict[step]['relative_rect_pos'][0])
        y_set.append(params_dict[step]['relative_rect_pos'][1])
    x_mean = round(statistics.mean(x_set), 3)
    y_mean = round(statistics.mean(y_set), 3)
    return ([x_mean, y_mean])


def write_in_json(filename, data):
    with open(f'accuracy_presets/{filename}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def calculate_mean_coeffs(data):
    alpha = 0
    beta = []
    gamma = []
    for step in data:
        a, b, g = data[step]['coeffs']
        if a != 0:
            alpha += a
        if b != 0:
            beta.append(b)
        if g != 0:
            gamma.append(g)
    result = [
        alpha,
        statistics.mean(beta),
        statistics.mean(gamma)]
    return result
