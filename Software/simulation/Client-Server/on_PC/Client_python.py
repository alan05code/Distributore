import serial 
from pyfirmata2 import Arduino, util
import time
from socket import *
serverName = 'localhost'
serverPort = 12000


arduino = serial.Serial(port='COM6', baudrate=9600, timeout=.1)

led_pins = [2, 3, 4, 5, 6, 7, 8, 9, 10]

def write(message):
    if isinstance(str(message), str):
        arduino.write(bytes(message, 'utf-8')) 
        time.sleep(0.05) 

def read():
    time.sleep(0.05)
    time.sleep(0.05)
    data = arduino.readline()
    time.sleep(0.05)
    if data!=b'':
        return data 

def RFID():
    code = read()
    if code is not None:
        return 1
    else:
        return 0
        
                
while True:
    check=RFID()
    if check:
        print (check)
    
mioSocket.close()
