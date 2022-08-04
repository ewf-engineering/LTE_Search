#!/usr/bin/env python3
import RPi.GPIO as GPIO
from gpiozero import LED, Button
from time import sleep
import numpy as np
import serial
import io
import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool

import logging
from multiprocessing import Process, JoinableQueue

from retry import retry
##Local Modules
import sys

import config
import GPSMain
import LTEMain
import Display
#CSURVF - Network Survey Format
#CSURVNLF - <CR><LF> Removing On Easy Scan® Commands Family
#CSURVBC - BCCH Network Survey (Numeric Format)
#CSURVUC - Network Survey Of User Defined Channels (Numeric Format)
#CSURVC - Network Survey (Numeric Format)
#CSURVEXT - Extended network survey
#ATE1 / ATE0

display_q = JoinableQueue()

#GPIO & Buttons
led = LED(27)
button = Button(22)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
buttons = [0,0,0,0]
def rotate_screen(button):
    global buttons
    buttons[0] = 1
    display_q.put(buttons)
    #buttons[0] = 0
GPIO.add_event_detect(12, GPIO.RISING, callback=rotate_screen, bouncetime=200)

logger = logging.getLogger('Search')
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter('%(asctime)s %(name)s: %(threadName)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)

#MySql Connect
def MySqlconnect():
    """ Connect to MySQL database """
    conn = None
    try:
        conn = mysql.connector.connect(host='localhost',
                                       database='LTE_Cells',
                                       user='admin',
                                       password='admin')
        if conn.is_connected():
            logger.info('Connected to MySQL database')
            cursor = conn.cursor()
            return cursor,conn
    except Error as e:
        logger.info(e)



#Serial Connection Setup
def SetupSerial():
    try:
        serialSetup = False
        while serialSetup == False:
            try:
                ser = serial.Serial()
                ser.baudrate = 115200
                ser.port = '/dev/ttyUSB2'
                ser.timeout = 5
                logger.info(ser)
                if (ser.is_open == False):
                    logger.debug("Serial Is_Open " + str(ser.is_open))
                    ser.open()
            except:
                logger.info('Error: Unable to Open Serial Connection!')
                sleep(2)
            finally:
                if ser.is_open:
                    sleep(1)
                    logger.info("Serial Open")
                    logger.info(ser)
                    #config.ser = ser
                    output = "ATE1" + '\r'
                    ser.write(output.encode())
                    sleep(.2)
                    logger.debug(ser.readline().decode('utf-8').rstrip())
                    sleep(.5)
                    if atcmd ("AT",ser):
                        return
    except Exception as e:
        logger.debug(traceback.print_exc())

def atcmd (cmd,ser):
    try:

        if ser.is_open:
            output = cmd + '\r'
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            ser.write(output.encode())
            while True:
                c = ser.readline().decode('utf-8').rstrip()
                logger.debug(c)
                if c == '':
                    logger.warning("No USB2 Response")
                    return False
                #logger.debug(gps.satInView)
                #if c!='':
                if ("OK" in c):
                    ser.close()
                    return True
    except Exception as e:
        logger.debug(traceback.print_exc())

if __name__ == "__main__":
    logger.info("--- Main ---")
    try:
        #cursor,conn = MySqlconnect()
        #cursor1,conn1 = MySqlconnect()
        con_pool = MySQLConnectionPool(pool_name='my_connection_pool',
                               pool_size=5,
                               host='localhost',
                               database='LTE_Cells',
                               user='admin',
                               password='admin')
        db_gps = con_pool.get_connection()
        cursor_gps = db_gps.cursor(buffered=True)
        db_lte = con_pool.get_connection()
        cursor_lte = db_lte.cursor(buffered=True)
        db_display = con_pool.get_connection()
        cursor_display = db_display.cursor(buffered=True)
        SetupSerial()

        #logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
        logger.info("Search.py MAIN!")
        SerialUSB2 = serial.Serial('/dev/ttyUSB2', 115200, timeout=1)
        SerialUSB1 = serial.Serial('/dev/ttyUSB1', 115200, timeout=1)

        #we Want USB1 to be setup before we start. Having a conflict on USB2 between the two processes will be a problem.
        logger.info("Check USB1")
        while GPSMain.checkStream(SerialUSB1,SerialUSB2,logger) == False:
            logger.info("USB1 EMPTY")
            GPSMain.checkStream(SerialUSB1,SerialUSB2,logger)
            sleep(1)
        logger.info("USB1 UP!")
        gps = Process(target=GPSMain.main, args=(cursor_gps,db_gps,SerialUSB1))
        lte = Process(target=LTEMain.main, args=(cursor_lte,db_lte,SerialUSB2))
        display = Process(target=Display.main,args=(display_q,cursor_display,db_display))
        #gps.start()
        #lte.start()
        display.start()
        while False:
            #Start GPS

            break
        #lte.join()
        #gps.join()
        display.join()
    except serial.SerialException as e:
        logger.info("SerialException")
        logger.info(e)
        exit()
    except KeyboardInterrupt:
        logger.info('interrupted!')
        config.ser.close()
        conn.close()
        cursor.close()
        lte.join()
        gps.join()
        display.join()
        exit()
#led.on()
