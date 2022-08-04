#!/usr/bin/env python3


# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time
import traceback
from datetime import datetime
import subprocess
from multiprocessing import Queue
import queue as q
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789
import logging
### Local Modules
import sys
import config
import LTE




logger = logging.getLogger('Display')
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter
#formatter = logging.Formatter('%(asctime)s %(name)s: %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
formatter = logging.Formatter('%(asctime)s %(name)s: %(levelname)s: %(message)s', datefmt='%I:%M:%S %p')

# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)

# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=240,
    height=240,
    x_offset=0,
    y_offset=80,
)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 180

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0


# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
gpsfont = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
cellfont = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

def rotate_screen():
    global rotation
    logger.debug("ROTATE SCREEN: %s", rotation)
    rotation += 90
    if rotation > 270:
        rotation = 0
def printCells(cursor,conn):
    try:
        x = 0
        y = 120 #Print 1/2 way down (240/2)
        LinesToPrint = 8
        i = 0
        output_earfcn_Xoffset   = 0
        output_rxLev_Xoffset    = 40
        output_mcc_Xoffset      = 35
        output_mnc_Xoffset      = 30
        output_rsrp_Xoffset     = 30
        output_rsrq_Xoffset     = 33
        output_cellID_Xoffset   = 35

        draw.text((x, y),"earfcn", font=cellfont, fill="#38E9C1"); x+=output_rxLev_Xoffset
        draw.text((x, y),"rxLev", font=cellfont, fill="#38E9C1"); x+=output_mcc_Xoffset
        draw.text((x, y),"MCC", font=cellfont, fill="#38E9C1"); x+=output_mnc_Xoffset
        draw.text((x, y),"MNC", font=cellfont, fill="#38E9C1"); x+=output_rsrp_Xoffset
        draw.text((x, y),"RSRP", font=cellfont, fill="#38E9C1"); x+=output_rsrq_Xoffset
        draw.text((x, y),"RSRQ", font=cellfont, fill="#38E9C1"); x+=output_cellID_Xoffset
        draw.text((x, y),"CellID", font=cellfont, fill="#38E9C1");

        y += cellfont.getsize(" ")[1]


        ## GET THE CELLS;
        logger.debug("Reading cells")
        sql_string = "select * from cells;"
        #logger.debug("conn_is_conn: %s",conn.is_connected())
        if conn.is_connected():
            logger.debug(conn.is_connected())
            cursor.execute(sql_string)
            conn.commit()
            value = str(cursor.fetchall()).strip("[]")
            logger.debug("cells = %s",len(value));
        value = value.split(")")
        if len(value) > 1:
            for line in value:
                line = line.strip(",").strip().strip("(")
                line = line.split(",")
                #logger.debug("value %s",line)
                x = 0 #Start at the left
                i += 1
                output_earfcn = str(line[0])
                draw.text((x, y),output_earfcn, font=cellfont, fill="#FF00FF")

                output_rxLev = str(line[1])
                x += output_rxLev_Xoffset
                draw.text((x, y),output_rxLev, font=cellfont, fill="#FF00FF")

                output_mcc = str(line[2])
                x += output_mcc_Xoffset
                draw.text((x, y),output_mcc, font=cellfont, fill="#FF00FF")

                output_mnc = str(line[3])
                x += output_mnc_Xoffset
                draw.text((x, y),output_mnc, font=cellfont, fill="#FF00FF")

                output_rsrp = str(line[8])
                x += output_rsrp_Xoffset
                draw.text((x, y),output_rsrp, font=cellfont, fill="#FF00FF")

                output_rsrq = str(line[9])
                x += output_rsrq_Xoffset
                draw.text((x, y),output_rsrq, font=cellfont, fill="#FF00FF")

                output_cellID = str(line[4])
                x += output_cellID_Xoffset
                draw.text((x, y),output_cellID, font=cellfont, fill="#FF00FF")

                #draw.text((x, y),str(output), font=font, fill="#FF00FF")
                y += cellfont.getsize(str(line))[1]

                if i==LinesToPrint:
                    break
        # Display image.
    except Exception as e:
        print(repr(e))
        traceback.print_exc()

def read_gps(cursor,conn):
    try:
        logger.debug("Reading GPS")
        sql_string = "select * from gps_status;"
        logger.debug("conn_is_conn: %s",conn.is_connected())
        if conn.is_connected():
            logger.debug(conn.is_connected())
            cursor.execute(sql_string)
            conn.commit()
            value = str(cursor.fetchall()).strip("[]").strip("()").replace("'","").replace(" ","")
            value = value.split(",")
            logger.debug("gps = %s",value);
            logger.debug(len(value))
            if len(value) > 1:
                return value
            else:
                return ['0', '0', "0", "N", "0", "W", '0', ' 1', ' 0', '0']
        else:
            value = ['0', '0', "0", "N", "0", "W", '0', ' 1', ' 0', '0']
            return value
        #value = value.split(")")
    except Exception as e:
        print(repr(e))
        traceback.print_exc()

def getIpAddress():
    cmd = "ifconfig wlan0"
    wlan0 = str(subprocess.check_output(cmd, shell=True).decode("utf-8").rstrip()).splitlines()
    #logger.debug(wlan0)
    for line in wlan0:
        #logger.debug(line)
        if "inet" in line:
            address = line.strip(" ").split(" ")
            logger.debug(address[1])
            return address[1]
def main(queue,cursor,conn):


    #SetupGPIO Pins
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    while True:
        try:
            try:
                queue_data = queue.get(block= False)
                logger.debug("Queue: %s",queue_data)
                if queue_data[0] == 1:
                    rotate_screen()
                queue.task_done()
            except q.Empty:
                logger.debug("Queue: ")

            except Exception as e:
                #logger.debug("Queue: ")
                traceback.print_exc()


            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")

            # Draw a black filled box to clear the image.
            draw.rectangle((0, 0, width, height), outline=0, fill=0)

            # Shell scripts for system monitoring from here:
            # https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
            cmd = "hostname -I | cut -d' ' -f1"
            IP = "IP: " + subprocess.check_output(cmd, shell=True).decode("utf-8")
            cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
            CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
            cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
            MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")
            cmd = 'df -h | awk \'$NF=="/"{printf "Disk: %d/%d GB  %s", $3,$2,$5}\''
            Disk = subprocess.check_output(cmd, shell=True).decode("utf-8")
            cmd = "cat /sys/class/thermal/thermal_zone0/temp |  awk '{printf \"CPU Temp: %.1f C\", $(NF-0) / 1000}'"  # pylint: disable=line-too-long
            Temp = subprocess.check_output(cmd, shell=True).decode("utf-8")
            cmd = "iwgetid -r"
            SSID = subprocess.check_output(cmd, shell=True).decode("utf-8").rstrip()
            #cmd = "sudo ifconfig wlan0 | sed -En -e 's/.*inet ([0-9.]+).*/\1/p'"
            #getIpAddress
            ipaddress =getIpAddress()
            #readGPS Status

            gps_values = read_gps(cursor,conn)

            # Write four lines of text.
            y = top
            x = 0
            #TIME
            draw.text((x, y), current_time, font=font, fill="#FFFFFF")
            y += font.getsize(current_time)[1]+2
            #WIFI
            draw.text((x, y), (str(SSID)+"@"+str(ipaddress)), font=gpsfont, fill="#519EEE")
            y += font.getsize(current_time)[1]


            #LAT
            draw.text((x, y), (str(gps_values[2]+str(gps_values[3]))), font=gpsfont, fill="#50B15D")
            #LONG
            draw.text((x+110, y), ("| " +str(gps_values[4]+str(gps_values[5]))), font=gpsfont, fill="#50B15D")
            y += font.getsize(current_time)[1]
            #ALT
            draw.text((x, y), ("ALT: " + str(gps_values[6])), font=gpsfont, fill="#50B15D")
            #Fix
            draw.text((x+80, y), ("Fix?: " + str(gps_values[7])), font=gpsfont, fill="#FF0000")
            #satInUse/satInView
            draw.text((x+140, y), ("Sat U|V: " + str(gps_values[8])+"|"+str(gps_values[9])), font=gpsfont, fill="#C15AC9")
            y += font.getsize(current_time)[1]



            #draw.text((x, y), str("NumSats: "+str(NumSats)), font=font, fill="#FFFFFF")
            #y += font.getsize(" ")[1]
            #draw.text((x, y), str("Location: "+str(LatestGPS)), font=cellfont, fill="#FFFFFF")
            #y += font.getsize(" ")[1]
            draw.text((x, y), CPU, font=font, fill="#FFFF00")
            y += font.getsize(CPU)[1]
            draw.text((x, y), Temp, font=font, fill="#FFFF00")
            y += font.getsize(Temp)[1]


            printCells(cursor,conn)

            disp.image(image, rotation)
            time.sleep(0.1)
        except Exception as e:
            backlight.value = False
            print(repr(e))
            traceback.print_exc()
            backlight.value = False
            GPIO.cleanup()
            exit()

if __name__ == "__main__":
    conn = config.MySqlconn
    cursor = conn.cursor(buffered=True)

    main(cursor,conn)
