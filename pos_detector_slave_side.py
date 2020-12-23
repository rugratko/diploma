import image, network, math, rpc, sensor, struct, tf, time, pyb
from pyb import LED

interface = rpc.rpc_usb_vcp_slave()

red_led   = LED(1)
green_led = LED(2)
blue_led  = LED(3)


sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time = 2000)


def find_center(x, y, w, h):
    return x + w/2, y + h/2


def restart(data):
    pyb.hard_reset()


def watcher(data):
    A = struct.unpack("<II", data)
    return struct.pack("<II", A[0], A[1])


def find_rectangle(data):
    time_stamp, size = struct.unpack("<II", data)
    img = sensor.snapshot()
    rectangles = img.find_rects(threshold = 20000)
    for r in rectangles:
        img = img.draw_rectangle(r.rect(), color = (255, 0, 0))
    if len(rectangles) == 2:
        x1, y1, x2, y2 = rectangles[0].x(), rectangles[0].y(), rectangles[1].x(), rectangles[1].y()
        w1, h1, w2, h2 = rectangles[0].w(), rectangles[0].h(), rectangles[1].w(), rectangles[1].h()
        pps = (w1 + h1 + w2 + h2)/(int(size)*4)
        dist = ((x2 - x1)**2 + (y2 - y1)**2) ** 0.5
        s1 = (w1+h1)/2
        s2 = (w2+h2)/2
        x1c, y1c = find_center(x1, y1, w1, h1)
        x2c, y2c = find_center(x2, y2, w2, h2)
        img = img.draw_line(round(x1c), round(y1c), round(x2c), round(y2c), color = (0, 0, 255), thickness = 1)
        filename = str(time_stamp) + '.bmp'
        img.save(filename, quality = 100)
        return struct.pack("<IIIIIIIII", time_stamp, (round((s1/pps)*10)), (round((s2/pps)*10)), (round((x1c/pps)*10)), (round((y1c/pps)*10)), ((round(x2c/pps)*10)), ((round(y2c/pps)*10)), round(pps), round(((dist/pps)*10)))
    return struct.pack("<IIIIIIIII", 0, 0, 0, 0, 0, 0, 0)


blue_led.on()
time.sleep_ms(1000)
blue_led.off()

red_led.on()
green_led.on()
blue_led.on()

interface.register_callback(watcher)
interface.register_callback(find_rectangle)
interface.register_callback(restart)

interface.loop()
