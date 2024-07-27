import serial
print(serial.__version__)




ser = serial.Serial('/dev/tty.usbmodem84722E74B66C1')
slider1 = 0
slider2 = 0
button_press = False

while True:
    momentary_reading = ser.readline(100).decode('utf-8')
    part1, part2, part3 = momentary_reading.split(sep = " ", maxsplit= 3)
    part1, part2 = float(part1), float(part2)
    part3, _ = part3.split("\r")
    part3 = part3.lower() in ["true"]
    print(type(part1), type(part2), type(part3), "\t" ,str(part1), "\t" , str(part2), "\t" ,str(part3))

ser.close()