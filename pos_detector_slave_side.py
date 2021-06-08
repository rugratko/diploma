import image, network, math, rpc, sensor, struct, tf, time, pyb
from pyb import LED

interface = rpc.rpc_usb_vcp_slave()

red_led = LED(1)
green_led = LED(2)
blue_led = LED(3)

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time=2000)


def find_center(x, y, w, h):
    return round(x+w/2), round(y+h/2)


def restart(data):
    pyb.hard_reset()


def watcher(data):
    A = struct.unpack("<II", data)
    return struct.pack("<II", A[0], A[1])


def make_shot(data):
    time_stamp, size = struct.unpack("<II", data)
    img = sensor.snapshot().lens_corr(1.8)
    filename = str(time_stamp) + '_correction.bmp'
    img.save(filename, quality=100)


def find_rectangle(data):
    time_stamp, size = struct.unpack("<II", data)
    img = sensor.snapshot().lens_corr(1.8)
    rectangles = img.find_rects(threshold=12500) #Проверить значение
    circles = img.find_circles(threshold=2750, x_margin=10, y_margin=10, r_margin=10, r_min=2, r_max=10, r_step=2)
    for r in rectangles:
        img = img.draw_rectangle(r.rect(), color=(0, 0, 255))
    for c in circles:
        img.draw_circle(c.x(), c.y(), c.r(), color=(50, 220, 100))
    if len(rectangles) == 1 and len(circles) == 4:
        rect_x, rect_y = rectangles[0].x(), rectangles[0].y()
        rect_w, rect_h = rectangles[0].w(), rectangles[0].h()
        circle1_x, circle1_y = circles[0].x(), circles[0].y()
        circle2_x, circle2_y = circles[1].x(), circles[1].y()
        circle3_x, circle3_y = circles[2].x(), circles[2].y()
        circle4_x, circle4_y = circles[3].x(), circles[3].y()
        rect_cx, rect_cy = find_center(rect_x, rect_y, rect_w, rect_h)
        filename = str(time_stamp) + '_step.bmp'
        img.save(filename, quality=100)
        return struct.pack(
            "<IIIIIIIIIII",
            time_stamp,
            rect_cx,
            rect_cy,
            circle1_x,
            circle1_y,
            circle2_x,
            circle2_y,
            circle3_x,
            circle3_y,
            circle4_x,
            circle4_y
        )

    return struct.pack("<IIIIIIIIIII", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)


blue_led.on()
time.sleep_ms(1000)
blue_led.off()

red_led.on()
green_led.on()
blue_led.on()

interface.register_callback(watcher)
interface.register_callback(make_shot)
interface.register_callback(find_rectangle)
interface.register_callback(restart)

interface.loop()
