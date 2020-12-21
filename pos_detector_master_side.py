import json, rpc, serial, serial.tools.list_ports, struct, sys, time
from datetime import datetime

print("\nAvailable Ports:\n")
for port, desc, hwid in serial.tools.list_ports.comports():
    print("{} : {} [{}]".format(port, desc, hwid))
interface = rpc.rpc_usb_vcp_master(port='COM6')
print("")
sys.stdout.flush()

def exe_marker_detection():
    result = interface.call("marker_detection")
    if result is not None and len(result):
        print("Checksum [A=%d, B=%d]" % struct.unpack("<HH", result))
            
def exe_find_rectangle():
    result = interface.call("find_rectangle")
    if result is None:
        print('None')
    if result is not None:
        print("Info: [s1 = %d, s2 = %d]:[dx = %d, dy = %d][PxSm = %d, Rg = %d]:" % struct.unpack("<HHHHHH", result))

def exe_snap_rectangle():
    result = interface.call("snap_rectangle")
    if result is None:
        print('None')
    if result is not None:
        name = "rectimg-%s.jpg" % datetime.now().strftime("%d.%m.%Y-%H.%M.%S")
        print("Writing rectimg %s..." % name)
        with open(name, "wb") as snap:
            snap.write(result)
    
while True:
    exe_marker_detection()
    exe_find_rectangle()
    exe_snap_rectangle()
    time.sleep(2)
