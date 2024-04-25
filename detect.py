import pupil_apriltags as pat
from pupil_apriltags import Detector
import cv2
import numpy as np
from oscpy.client import OSCClient

c_freq = 261.6 # position 24
start_freq = c_freq*(125*8)/(27*64) #position 0
lower_limit = 100 #lower limit for frequencies, will be doubled
upper_limit = 500 #upper limit for frequencies, will be halved

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


for i in range(0,7):
    # keep frequencies in limits
    freq_array[0, i] = start_freq * ((5**i)/(4**i))
    freq_array[0, i] = check_limits(freq_array[0, i], lower_limit, upper_limit)     

for j in range(0, 11):
    for i in range(0,7):
        freq_array[j, i] = freq_array[0, i] * ((3**j)/(2**j))
        freq_array[j, i] = check_limits(freq_array[j, i], lower_limit, upper_limit)

print(freq_array)

OSC_HOST ="127.0.0.1" #127.0.0.1 is for same computer
OSC_PORT = 8000
OSC_CLIENT = OSCClient(OSC_HOST, OSC_PORT)

#height = 900
#width = 700
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

    #convert to gray
    bw_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    
   

    #flatten freq_array for easier acces + have a list from which to remove elements
    flat_frequencies = freq_array.flatten()
  
    results = at_detector.detect(bw_frame)
    result_tags = [r.tag_id for r in results]
    for result in results:

        a = np.int32(result.corners)
        frame = cv2.drawContours(frame, [a], 0, (0,0,255), 2)
        frame = cv2.putText(frame, str(result.tag_id), (int(result.center[0]),int(result.center[1])), cv2.FONT_HERSHEY_SIMPLEX ,  
                   1, (0, 255, 0), 1, cv2.LINE_AA)
    
    ## slice the green
    
    #
    
    #cv2.imshow('Image Feed', red)
    cv2.imshow('Image Feed', frame)
    
    
    # SEND OSC 
    if cv2.waitKey(10) & 0xFF == ord('x'):
        for indx, freq in enumerate(flat_frequencies):
            string_path = '/instrument'
            ruta = string_path.encode()
            if indx in result_tags:
                OSC_CLIENT.send_message(ruta,  [float(indx), float(0)])
                #print("ON", flat_frequencies[indx]) 
            else:
                OSC_CLIENT.send_message(ruta, [float(indx), float(freq)])
                #print("OFF:", flat_frequencies[indx])

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break
        
cap.release()
cv2.destroyAllWindows()
cv2.waitKey(1)