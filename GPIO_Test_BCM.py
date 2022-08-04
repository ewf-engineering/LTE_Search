#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time

def rotate_screen(button):
    print("ROTATE")

GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(12, GPIO.RISING, callback=rotate_screen, bouncetime=200)



try:
    while True:
        #print(GPIO.input(21))
        if GPIO.input(21) == False:
            print("21 ", end='')
        if GPIO.input(20) == False:
            print("20 ", end='')

        if GPIO.input(12) == False:
            print("12 ", end='')


        if GPIO.input(5) == False:
            print("05 ", end='')
        if GPIO.input(6) == False:
            print("06 ", end='')
        if GPIO.input(13) == False:
            print("13 ", end='')
        #if GPIO.input(19) == False:
        #    print("19")
        if GPIO.input(7) == False:
            print("07 ", end='')
        if GPIO.input(16) == False:
            print("16 ", end='')
        print("")
        time.sleep(.2)
except Exception as e:
    raise
