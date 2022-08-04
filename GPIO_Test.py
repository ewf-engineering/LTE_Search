#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BOARD)
GPIO.setup(40, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(38, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(36, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(32, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(29, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(31, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(33, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(35, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(37, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        #print(GPIO.input(40))
        if GPIO.input(40) == False:
            print("40 ", end='')
        if GPIO.input(38) == False:
            print("38 ", end='')
        if GPIO.input(36) == False:
            print("36 ", end='')
        if GPIO.input(32) == False:
            print("32 ", end='')


        if GPIO.input(29) == False:
            print("29 ", end='')
        if GPIO.input(31) == False:
            print("31 ", end='')
        if GPIO.input(33) == False:
            print("33 ", end='')
        #if GPIO.input(35) == False:
        #    print("35")
        if GPIO.input(16) == False:
            print("16 ", end='')
        if GPIO.input(18) == False:
            print("18 ", end='')
        if GPIO.input(26) == False:
            print("26 ", end='')
        print("")
        time.sleep(.2)
except Exception as e:
    raise
