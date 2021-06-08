k_amp = 200
k_adc = 65536 / 5
U_s = 5


def get_alpha(data, weight):
    alpha = data / (weight / 1000 * 9.81 * k_adc * k_adc * U_s)
    return alpha


def get_beta(data, weight, x, alpha):
    beta = (data - alpha * weight / 1000 * 9.81) / (weight / 1000 * 9.81 * x /
                                                    1000 * k_adc * k_adc * U_s)
    return beta


def get_gamma(data, weight, y, alpha):
    gamma = (data - alpha * weight / 1000 * 9.81) / (
        weight / 1000 * 9.81 * y / 1000 * k_adc * k_adc * U_s)
    return gamma


def get_weight_scaling(data, alpha, beta, gamma, x, y):
    weight = data / (9.81 * k_adc * k_adc * U_s *
        (alpha + beta * x / 1000 + gamma * y / 1000))
    weight_wo_corr = data / (9.81 * alpha * k_adc * k_adc * U_s)
    return weight, weight_wo_corr