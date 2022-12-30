#!/usr/bin/env python3

import os
import time
import RPi.GPIO as GPIO
import pigpio
import socket
import pickle

pan_pin = 18
pan_dutycycle = 1500.0
pan_speed = 0.0

UDP_IP = "127.0.0.1"
UDP_PORT = 60504

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.setblocking(0)


try:
    f = open("ptcontrol-presets.pkl", 'rb')
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


pwm = pigpio.pi()
pwm.set_mode(pan_pin, pigpio.OUTPUT)

pwm.set_PWM_frequency( pan_pin, 100)
pwm.set_servo_pulsewidth(pan_pin, pan_dutycycle)


while True:
    pan_dutycycle += pan_speed
    pan_dutycycle = minmax(pan_dutycycle, 600, 2350)
    pwm.set_servo_pulsewidth(pan_pin, pan_dutycycle)
    
    try:
        data, addr = sock.recvfrom(1024)
    except:
        data = ""
    
    if len(data):
        data = data.decode("utf-8")
        datasplit = data.split(":")
        if datasplit[0] == "PT":
            pan = float(datasplit[1])
            pan_speed = pan*0.5

        if datasplit[0] == "SP":
            Presets[int(datasplit[1])] = pan_dutycycle
            f = open("ptcontrol-presets.pkl", 'wb')
            pickle.dump(Presets, f)
            f.close()
            
        if datasplit[0] == "RP":
            pan_dutycycle = Presets[int(datasplit[1])]
        
        print("received message: %s" % data)
    time.sleep(0.001)
    

