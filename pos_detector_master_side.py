import rpc, serial, serial.tools.list_ports, struct, sys, time, json
from datetime import datetime

def connect_usb():
    print("\nAvailable Ports:\n")
    for port, desc, hwid in serial.tools.list_ports.comports():
        print("{} : {} [{}]".format(port, desc, hwid))
    interface = rpc.rpc_usb_vcp_master(port='COM6')
    print("")
    sys.stdout.flush()
    return interface


def dict_dumper(params):
    buff = {'timestamp':params[0],
            'size':[params[1], params[2]],
            'center_1':[params[3], params[4]],
            'center_2':[params[5], params[6]],
            'pixels_per_cm':params[7],
            'range':params[8]}
    data.append(buff)


def exe_watcher(interface):
    time_stamp_s = int(datetime.now().strftime('%S'))
    time_stamp_m = int(datetime.now().strftime('%M'))
    print('Sent %d %d' % (time_stamp_s, time_stamp_m))
    result = interface.call("watcher", struct.pack('<II', time_stamp_s, time_stamp_m))
    if result is not None and len(result):
        print("Checksum [A=%d, B=%d]" % struct.unpack("<II", result))

            
def exe_find_rectangle(interface, size):
    time_stamp = int(datetime.now().strftime('%H%M%S'))
    time_stamp_packed = struct.pack('<II', time_stamp, size)
    result = interface.call("find_rectangle", time_stamp_packed)
    if result is None:
        print('None')
    if result is not None:
        params = struct.unpack("<IIIIIIIII", result)
        if params[0] != 0:
            print("Info: [ts = %d][s1 = %d, s2 = %d][x1c = %d, y1c = %d][x2c = %d, y2c = %d][PxCm = %d, Rg = %d]:" % struct.unpack("<IIIIIIIII", result))
            dict_dumper(params)
            
            
def exe_restart(interface):
    interface.call("restart")

i = 0
k = 0
sensor = 'test_sensor'
calibration_map = {sensor:[]}
data = []
interface = connect_usb()  
size = 2

while True:
    i += 1
    exe_watcher(interface)
    exe_find_rectangle(interface, size)
    time.sleep(0.5)
    if i == 4:
        try:
            exe_restart(interface)
        except:
            i = 0
            time.sleep(3)
            iteration = 'Step %d' % k
            calibration_map[sensor].append({iteration:data.copy()})
            data.clear()
            a = int(input('1 for new iteration, 0 to stop: '))
            if a:
                k += 1
                interface = connect_usb()
            else:
                with open('data.json', 'w') as outfile:
                    outfile.write(json.dumps(calibration_map, indent=4))
                exit()
        
