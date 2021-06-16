def get_alpha(data, weight):
    alpha = data / (weight / 1000 * 9.81)
    return alpha


def get_beta(data, weight, x, alpha):
    beta = (data - alpha * weight / 1000 * 9.81) / (weight / 1000 * 9.81 * x /
                                                    1000)
    return beta


def get_gamma(data, weight, y, alpha):
    gamma = (data - alpha * weight / 1000 * 9.81) / (
        weight / 1000 * 9.81 * y / 1000)
    return gamma


def get_weight_scaling(data, alpha, beta, gamma, x, y):
    weight = data / (9.81 * 
        (alpha + beta * x / 1000 + gamma * y / 1000))
    weight_wo_corr = data / (9.81 * alpha)
    return weight, weight_wo_corr