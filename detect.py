import pupil_apriltags as pat
from pupil_apriltags import Detector
import cv2
import numpy as np
from oscpy.client import OSCClient
import serial
import math
import time

c_freq = 261.63 # position 24
c_midi = 60
start_freq = c_freq*(125*8)/(27*64) #position 0
start_midi = c_midi - 9
lower_limit = 100 #lower limit for frequencies, will be doubled
upper_limit = 500 #upper limit for frequencies, will be halved

def mean(array):
    return sum(array)/len(array)

def midi_to_freq(midi_val):
    return 440 * pow(2, (midi_val -69)/12)

def freq_to_midi(freq_val):
    return 12*math.log2(freq_val/440) + 69

def closest_octave(var, fix):
    # should return the closest frequency in an octave relation of the midi note to the 5-limit frequency
    # fix = the value from the 5-lim frequency array, the "goal"
    # var = the frequency calculated from the midi array
    # closest_octave(261.6, 260)
    var_m = freq_to_midi(var)
    fix_m = freq_to_midi(fix)

    if fix_m - var_m < -6:
        return closest_octave(var/2, fix)
    if fix_m - var_m > 6:
        return closest_octave(var*2, fix)
    else:
        return midi_to_freq(var_m)

def check_limits(value, lower_lim, upper_lim):
    if value < lower_limit:
        value = value*2
    if value > upper_lim:
        value = value/2
    
    if value < lower_limit:
        value = check_limits(value, lower_limit, upper_lim)
        return value
    if value > upper_lim:
        value = check_limits(value, lower_limit, upper_lim)
        return value
    else:
        return value
    


freq_array = np.zeros((11, 7))
midi_array = np.zeros((11, 7))
midi_freq_array = np.zeros((11, 7))


for i in range(0,7):
    # keep frequencies in limits
    freq_array[0, i] = start_freq * ((4**i)/(5**i))
    freq_array[0, i] = check_limits(freq_array[0, i], lower_limit, upper_limit)
    midi_array[0, i] = (start_midi - 4*i)

freq_array = np.fliplr(freq_array)
midi_array = np.fliplr(midi_array)

print("\n")
print("FREQ 5limit 1 row ")
print("\n")
print(np.round(freq_array, 2))
print("\n")
print("FREQ 12TET 1 row ")
print("\n")
print(np.round(midi_to_freq(midi_array), 2))
print("\n")

for j in range(0, 11):
    for i in range(0,7):
        freq_array[j, i] = freq_array[0, i] * ((3**j)/(2**j))
        freq_array[j, i] = check_limits(freq_array[j, i], lower_limit, upper_limit)
        midi_array[j, i] = midi_array[0, i] + 7*j
        
print("\n")
print("FREQ 5limit full ")
print("\n")
print(np.round(freq_array, 2))
print("\n")
print("FREQ 12TET full before matching ")
print("\n")
print(np.round(midi_to_freq(midi_array), 2))
print("\n")

for i in range(0, 7):
    for j in range(0, 11):
        midi_freq_array[j, i] = closest_octave(midi_to_freq(midi_array[j, i]), freq_array[j, i])

print("FREQ 12TET full & matched")
print("\n")
print(np.round(midi_freq_array, 2))
print("\n")

print("DEVIATION 12tet TO 5-LIM")
print(np.round(freq_array - midi_freq_array, 2))

OSC_HOST ="127.0.0.1" #127.0.0.1 is for same computer
OSC_PORT = 8000
OSC_CLIENT = OSCClient(OSC_HOST, OSC_PORT)

try:
    ser = serial.Serial('/dev/tty.usbmodem84722E74B66C1')
    print(ser.name, ser.is_open)
except:
    ser = "empty"
    print("No serial connected!")
len_ma = 3 # moving average of length len_ma
slider1 = 0
slider1_array = [0] * len_ma
slider2 = 0
slider2_array = [0] * len_ma
button_press = False


height = 800
width = 1300

board = {}
board_initialized = False

at_detector = Detector(
   families="tag36h11",
   nthreads=1,
   quad_decimate=1.0,
   quad_sigma=0.0,
   refine_edges=1,
   decode_sharpening=0.25,
   debug=0
)

# Paths OSC
path_5lim = '/instrument'
path_12TET = '/instrument_12tet'
path_morph = '/morph_factor'
path_volume = '/volume'
ruta_5lim = path_5lim.encode()
ruta_12TET = path_12TET.encode()
ruta_morph = path_morph.encode()
ruta_volume = path_volume.encode()


# running index wrapping around 
running_index = 0

old_morph_factor = 0
old_volume = 0

try:
    momentary_reading = ser.readline(100).decode('utf-8')
    print("Serial connection established")
except ValueError as e:
    print("ValueError, check serial output of microcontroller")
except AttributeError:
    print("Probably not connected to serial!")

# VIDEO FEED
cap = cv2.VideoCapture(0)
while cap.isOpened():
    
    ret, frame = cap.read()
    center = frame.shape
    x = center[1]/2 - width/2
    y = center[0]/2 - height/2
    frame = frame[int(y):int(y+height), int(x):int(x+width)]

    # flip
    frame = cv2.flip(frame, 0)
    frame = cv2.flip(frame, 1)

    # convert to gray
    bw_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


    try:
        momentary_reading = ser.readline(100).decode('utf-8')
        part1, part2, part3 = momentary_reading.split(sep = " ", maxsplit= 3)
        slider1, slider2 = float(part1), float(part2)
        part3, _ = part3.split("\r")
        button_press = part3.lower() in ["true"]
    except ValueError as e:
        
        part1, part2, part3 = slider1, slider2, button_press
    except AttributeError:
        part1, part2, part3 = slider1, slider2, button_press
    
    
    # mapping sliders to send to csound
    # max at 3V = 53262 
    # leaving some headroom, playable range = [0.05 - 0.95]
    slider1_array[running_index] = (min(max((slider1/53262), 0.05), 0.95) - 0.05)/0.9
    slider2_array[running_index] =  (min(max((slider2/53262), 0.05), 0.95) - 0.05)/0.9
    

    morph_factor = round(mean(slider2_array), 2)
    volume = round(mean(slider1_array), 2)
    if morph_factor != old_morph_factor:
        OSC_CLIENT.send_message(ruta_morph, [float(morph_factor)])
        old_morph_factor = morph_factor
    if volume != old_volume:
        OSC_CLIENT.send_message(ruta_volume, [float(volume)])
        old_volume = volume
    

    # flatten freq_array for easier acces + have a list from which to remove elements
    flat_frequencies = freq_array.flatten()
    flat_midi_frequencies = midi_freq_array.flatten()
    
    # detect fiducial markers from black-and-white frame
    results = at_detector.detect(bw_frame)
    result_tags = [r.tag_id for r in results]
    
    # draw contour around fiducial markers and add ids
    for result in results:
        a = np.int32(result.corners)
        frame = cv2.drawContours(frame, [a], 0, (0,0,255), 2)
        frame = cv2.putText(frame, str(result.tag_id), (int(result.center[0]),int(result.center[1])), cv2.FONT_HERSHEY_SIMPLEX ,  
                   1, (0, 255, 0), 1, cv2.LINE_AA)
    
    cv2.imshow('Image Feed', frame)
    
    # SEND OSC if button is pressed or 'x' key is pressed    
    if button_press or (cv2.waitKey(10) & 0xFF == ord('x')):                           
        print("press")
        for indx, (freq, midi_freq) in enumerate(zip(flat_frequencies, flat_midi_frequencies)):
            if indx in result_tags:
                OSC_CLIENT.send_message(ruta_5lim,  [float(indx), float(0)])
                OSC_CLIENT.send_message(ruta_12TET,  [float(indx), float(0)])
            else:
                OSC_CLIENT.send_message(ruta_5lim, [float(indx), float(freq)])
                OSC_CLIENT.send_message(ruta_12TET, [float(indx), float(midi_freq)])


    if cv2.waitKey(10) & 0xFF == ord('q'):
        break
        
    running_index= (running_index + 1)%len(slider1_array)

    
cap.release()
cv2.destroyAllWindows()
cv2.waitKey(1)