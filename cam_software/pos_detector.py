import drivers.rpc as rpc, serial, serial.tools.list_ports, struct, sys, time, json
from operator import itemgetter
from datetime import datetime
from math import sqrt, pow


def connect_usb():
    print("\nAvailable Ports:\n")
    for port, desc, hwid in serial.tools.list_ports.comports():
        print("{} : {} [{}]".format(port, desc, hwid))
    interface = rpc.rpc_usb_vcp_master(port='COM5')
    print("")
    sys.stdout.flush()
    return interface


def sort_by_pos(params):
    params.sort(key=lambda coord: (sqrt(pow(coord[0],2) + pow(coord[1],2)), coord[1]))
    return params


def calculate_ratio(params_dict):
    c1x, c1y = params_dict['circle1_pos']
    c2x, c2y = params_dict['circle2_pos']
    c3x, c3y = params_dict['circle3_pos']
    c4x, c4y = params_dict['circle4_pos']
    print(c1x, c1y, c2x, c2y, c3x, c3y, c4x, c4y)
    pix_per_mm_ratio = ((c3x - c1x) + (c2y - c1y) + (c4x - c2x) +
                        (c4y - c3y)) / (4 * 120)
    return pix_per_mm_ratio


def calculate_platform_center(params_dict):
    c1x, c1y = params_dict['circle1_pos']
    c2x, c2y = params_dict['circle2_pos']
    c3x, c3y = params_dict['circle3_pos']
    c4x, c4y = params_dict['circle4_pos']
    half_len_x = ((c3x - c1x) + (c4x - c2x)) / 4
    half_len_y = ((c2y - c1y) + (c4y - c3y)) / 4
    center_x = ((c1x + c2x) / 2) + half_len_x
    center_y = ((c1y + c3y) / 2) + half_len_y
    return ([center_x, center_y])


def calculate_relative_rect_pos(params_dict):
    rect_cx, rect_cy = params_dict['rect_pos']
    center_x, center_y = params_dict['platform_center']
    pix_per_mm = params_dict['pixel_per_mm_ratio']
    rel_x = (rect_cx - center_x)/pix_per_mm
    rel_y = (rect_cy - center_y)/pix_per_mm
    return ([rel_x, rel_y])


def dict_dumper(params):
    buff = {
        'timestamp': params[0],
        'rect_pos': [params[1], params[2]]}
    pos_list = [[params[3], params[4]], [params[5], params[6]], [params[7], params[8]], [params[9], params[10]]]
    sorted_list = sort_by_pos(pos_list)
    buff['circle1_pos'] = sorted_list[0]
    buff['circle2_pos'] = sorted_list[1]
    buff['circle3_pos'] = sorted_list[2]
    buff['circle4_pos'] = sorted_list[3]
    buff['pixel_per_mm_ratio'] = calculate_ratio(buff)
    buff['platform_center'] = calculate_platform_center(buff)
    buff['relative_rect_pos'] = calculate_relative_rect_pos(buff)
    print(buff)
    return(buff)


def exe_watcher(interface):
    time_stamp_s = int(datetime.now().strftime('%S'))
    time_stamp_m = int(datetime.now().strftime('%M'))
    print('Sent %d %d' % (time_stamp_s, time_stamp_m))
    result = interface.call("watcher", struct.pack('<II', time_stamp_s, time_stamp_m))
    if result is not None and len(result):
        print("Checksum [A=%d, B=%d]" % struct.unpack("<II", result))


def exe_find_rectangle(interface):
    time_stamp = int(datetime.now().strftime('%H%M%S'))
    time_stamp_packed = struct.pack('<II', time_stamp, 1)
    result = interface.call("find_rectangle", time_stamp_packed)
    if result is None:
        print('None')
    if result is not None:
        print(len(result))
        params = struct.unpack("<IIIIIIIIIII", result)
        if params[0] != 0:
            return(dict_dumper(params))
        else:
            return False


def make_shot():
    interface = connect_usb()
    time_stamp = int(datetime.now().strftime('%H%M%S'))
    result = interface.call("make_shot", struct.pack('<II', time_stamp, 1))
    time.sleep(1)
    try:
        exe_restart(interface)
    except Exception:
        print('Camera has been rebooted')
        time.sleep(5)


def exe_restart(interface):
    interface.call("restart")
    interface = connect_usb()


def shot_series(interface, n_shots=3):
    data = {}
    for i in range(n_shots):
        exe_watcher(interface)
        while True:
            result = exe_find_rectangle(interface)
            if result:
                break
        data[f'Shot {i+1}'] = result
        print(f'Stage {i+1} has been completed\n')
        time.sleep(1)
    print(data)
    return(data)


def connect_to_camera(shots):
    time.sleep(2)
    result = shot_series(interface, shots)
    time.sleep(1)
    try:
        exe_restart(interface)
    except Exception:
        print('Camera has been rebooted')
        time.sleep(5)
    return result


def connect_to_camera_wo_reboot(shots):
    time.sleep(2)
    result = shot_series(interface, shots)
    time.sleep(2)
    return result


interface = connect_usb()