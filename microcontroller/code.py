import analogio
from analogio import AnalogIn
from digitalio import DigitalInOut
import board
import time

fader0 = AnalogIn(board.A0)
fader1 = AnalogIn(board.A1)
switch = DigitalInOut(board.A2)
switch_value = 0
last_switch_value = 0



while True:
    a = fader0.value 
    time.sleep(0.01)
    b = fader1.value
    time.sleep(0.01)
    switch_value = (not switch.value )* 1
    click = switch_value - last_switch_value == -1
    
    
    
    time.sleep(0.01)
    print(a, b, click)
    last_switch_value = switch_value
    time.sleep(0.1)
    

