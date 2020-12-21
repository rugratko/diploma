import image, network, math, rpc, sensor, struct, tf, time
from pyb import LED

interface = rpc.rpc_usb_vcp_slave()

green_led = LED(2)
blue_led  = LED(3)

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time = 2000)

def marker_detection(data):
    return struct.pack("<HH", 5, 10)


def find_rectangle(data):
    img = sensor.snapshot()
    rectangles = img.find_rects(threshold = 20000)
    if len(rectangles) == 2:
        x1, y1, x2, y2 = rectangles[0].x(), rectangles[0].y(), rectangles[1].x(), rectangles[1].y()
        w1, h1, w2, h2 = rectangles[0].w(), rectangles[0].h(), rectangles[1].w(), rectangles[1].h()
        pps = (w1 + h1 + w2 + h2)/8
        dist = ((x2 - x1)**2 + (y2 - y1)**2) ** 0.5
        s1 = (w1+h1)/2
        s2 = (w2+h2)/2
        dx = (x2 - x1)
        dy = (y2 - y1)
        return struct.pack("<HHHHHH", round(s1/pps), round(s2/pps), round(dx/pps), round(dy/pps), round(pps), round(dist/pps))
    return struct.pack("<HHHHHH", 0, 0, 0, 0, 0, 0)


def snap_rectangle(data):
    img = sensor.snapshot()
    rectangles = img.find_rects(threshold = 20000)
    for r in rectangles:
        img = img.draw_rectangle(r.rect(), color = (255, 0, 0))
    return img.compress(quality = 90).bytearray()


blue_led.on()
time.sleep_ms(1000)
blue_led.off()


interface.register_callback(marker_detection)
interface.register_callback(find_rectangle)
interface.register_callback(snap_rectangle)

interface.loop()
