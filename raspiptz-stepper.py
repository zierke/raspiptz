#!/usr/bin/env python3

# sudo pip3 install rpimotorlib


import os
import time
import RPi.GPIO as GPIO
import pigpio
import socket
import pickle
import math

import advpistepper

GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.IN)

driver = advpistepper.Driver28BYJ48(pink=23, orange=25, yellow=24, blue=8)
stepper = advpistepper.AdvPiStepper(driver)

pan_dutycycle = -539 # Steps from home position to middle
pan_speed = 0.0

UDP_IP = "127.0.0.1"
UDP_PORT = 60504

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.setblocking(0)

Release_Timer = time.time()

try:
    f = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "raspiptz-presets.pkl"), 'rb')
    Presets = pickle.load(f)
    f.close()

except:
    Presets = {}


def minmax(value, min_v, max_v):
    if value < min_v:
        return min_v
    if value > max_v:
        return max_v
    return value

# Auto home to the left until hall effect sensor is 
while GPIO.input(21):
    stepper.move(1)
stepper.zero()

while True:

    pan_dutycycle += pan_speed
    #pan_dutycycle = minmax(pan_dutycycle, -2*539, 0)
    stepper.move_to(int(pan_dutycycle))

    if stepper.is_running == True:
        Release_Timer = time.time()
        
    if time.time() - Release_Timer > 1: 
        stepper.release()
        
    try:
        data, addr = sock.recvfrom(1024)
    except:
        data = ""
    
    if len(data):
        data = data.decode("utf-8")
        datasplit = data.split(":")
        if datasplit[0] == "PT":
            pan = float(datasplit[1])
            pan_speed = pan * 1

        if datasplit[0] == "SP":
            Presets[int(datasplit[1])] = pan_dutycycle
            f = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "raspiptz-presets.pkl"), 'wb')
            pickle.dump(Presets, f)
            f.close()
            
        if datasplit[0] == "RP":
            pan_dutycycle = Presets[int(datasplit[1])]
            
        
        print("received message: %s" % data)
    time.sleep(0.001)
    

