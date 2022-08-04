#!/usr/bin/env python3
from time import sleep
import traceback
import serial
import mysql.connector
import logging
import multiprocessing
#local Modules
import sys
import config

from ErrorLogging import *
LogHed_GPS = config.LogHed_GPS

logger = logging.getLogger('GPS')
logger.setLevel(logging.INFO)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter
#formatter = logging.Formatter('%(asctime)s %(name)s: %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
formatter = logging.Formatter('%(asctime)s %(name)s: %(levelname)s: %(message)s', datefmt='%I:%M:%S %p')

# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)

class gpsStatus:
    time:       float # $GPGGA[1] UTC
    lat:        float # $GPGGA[2]
    lat_dir:    str # $GPGGA[3]
    lng:       float # $GPGGA[4]
    lng_dir:   str # $GPGGA[5]
    gpsFix:     int # $GPGGA[6]
    satInUse:   int # $GPGGA[7]
    alt:        float # $GPGGA[9]
    satInView:  int #GPGSV[3]
    #def __init__(self, time,lat,lat_dir,lng,lng_dir,gpsFix,satInUse,alt,satInView):
    def __init__(self):
        self.time = 0#      float # $GPGGA[1] UTC
        self.lat  = 0#   float # $GPGGA[2]
        self.lat_dir = 'N'#   str # $GPGGA[3]
        self.lng = 0#       float # $GPGGA[4]
        self.lng_dir = 'W'#   str # $GPGGA[5]
        self.gpsFix = 0#     int # $GPGGA[6]
        self.satInUse =0#   int # $GPGGA[7]
        self.alt = 0#        float # $GPGGA[9]
        self.satInView = 0#  int #GPGSV[3]
def readGPSstream(cursor,conn,ser1,logger):
    try:
        #ser1.open()c
        gps = gpsStatus()
        if(ser1.is_open):
            logger.debug("is_open")
            ser1.timeout = 2
            ser1.reset_input_buffer()
            ser1.reset_output_buffer()
            sleep(.1)
            while True:
                c = ser1.readline().decode('utf-8').rstrip().split(',')
                logger.debug(c)
                if c != '' and c[0] == '$GPGGA':
                    #logger.debug("$GPGGA")
                    if c[1] != '':
                        gps.time = c[1]
                    if c[2] != '':
                        gps.lat  = c[2]
                    if c[3] != '':
                        gps.lat_dir = c[3]
                    if c[4] != '':
                        gps.lng = c[4]
                    if c[5] != '':
                        gps.lng_dir = c[5]
                    if c[6] != '':
                        gps.gpsFix = c[6]
                    if c[7] != '':
                        gps.satInUse = c[7]
                    if c[9] != '':
                        gps.alt = c[9]
                    #logger.debug(gps.time)
                    WriteGPSStatus(gps,cursor,conn)
                if c!='' and c[0] == '$GPGSV':
                    #logger.debug("$GPGSV")
                    gps.satInView = c[3]
                elif c[0] == '':
                    logger.warning("No USB1 Stream!!")
                    #GpsSetup(ser2)
                #logger.debug(gps.satInView)
                #if c!='':

    except Exception as e:
        logger.debug(traceback.print_exc())
        logger.debug(e)
        exit()

def checkStream(ser1,ser2,logger):
    try:
        #ser1.open()c
        if(ser1.is_open):
            logger.debug("is_open")
            ser1.timeout = 2
            ser1.reset_input_buffer()
            ser1.reset_output_buffer()
            sleep(.1)
            while True:
                c = ser1.readline().decode('utf-8').rstrip().split(',')
                logger.debug(c)

                if c[0] == '':
                    logger.warning("No USB1 Stream!!")
                    GpsSetup(ser2)
                    return False
                #logger.debug(gps.satInView)
                #if c!='':
                if c[0] != '':
                    return True
    except Exception as e:
        logger.debug(traceback.print_exc())
        logger.debug(e)
        exit()


def WriteGPSStatus(gps,cursor,conn):
    try:
        logger.debug("WriteGPSSTATUS")
        values = [gps.time,
                    gps.lat,
                    gps.lat_dir,
                    gps.lng,
                    gps.lng_dir,
                    gps.alt,
                    gps.gpsFix,
                    gps.satInUse,
                    gps.satInView,1]

        logger.info(values)
        #ID int,
        ##time float,
        #lat float,
        #lat_dir char,
        #lng float,
        #lng_dir char,
        #gpsFix int,
        #satInUse int,
        #alt float,
        #satInView int)
        cursor.execute("UPDATE low_priority gps_status SET time = %s,lat = %s,lat_dir = %s,lng = %s,lng_dir = %s,gpsFix = %s,satInUse = %s,alt = %s,satInView = %s where ID = %s ",(gps.time,gps.lat,gps.lat_dir,gps.lng,gps.lng_dir,gps.gpsFix,gps.satInUse,gps.alt,gps.satInView,  1))


        #cursor.execute("UPDATE gps_status SET time = %s where ID = %s LOCK IN SHARE MODE",(gps.time, 1))
        #cursor.execute("UPDATE gps_status SET lat = %s where ID = %s",(gps.lat, 1))
        #cursor.execute("UPDATE gps_status SET lat_dir = %s where ID = %s",(gps.lat_dir, 1))
        #cursor.execute("UPDATE gps_status SET lng = %s where ID = %s",(gps.lng, 1))
        #cursor.execute("UPDATE gps_status SET lng_dir = %s where ID = %s",(gps.lng_dir, 1))
        #cursor.execute("UPDATE gps_status SET gpsFix = %s where ID = %s",(gps.gpsFix, 1))
        #cursor.execute("UPDATE gps_status SET satInUse = %s where ID = %s",(gps.satInUse, 1))
        #cursor.execute("UPDATE gps_status SET alt = %s where ID = %s",(gps.alt, 1))
        #cursor.execute("UPDATE gps_status SET satInView = %s where ID = %s",(gps.satInView, 1))
        conn.commit()
        logger.debug("Sucessfuly Wrote GPS data to server")
    except mysql.connector.Error as error:
        logger.debug("Failed to insert record into MySQL table {}".format(error))
        if ("Broken Pipe" in str(error)):
            exit()
        logger.debug(values)

def getGPS(cmd,ser,timeout,cursor,conn):
    LogHed_GPS = config.LogHed_GPS
    if(ser.is_open):
        logger.debug("is_open")
        ser.timeout = timeout
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        sleep(0.5)
        output = cmd + '\r'
        ser.write(output.encode())
        sleep(.25)
        #logger.debug('>>>Ser: Read...')
        SerGPS = "[Ser2: GPS] "
        data = []
        try:
            while True:
                c = ser.readline().decode('utf-8').rstrip()
                if ('ended' in str(c)):
                    logger.debug( str(c))
                    break
                elif('ERROR' in str(c)):
                    logger.debug(str(c))
                    break
                elif('OK' in str(c)):
                    logger.debug(str(c))
                    break
                elif('$GPSACP:' in str(c)):
                    logger.debug(str(c))
                    c = c.removeprefix('$GPSACP:')
                    if c == '':
                        raise GPSNotSetup
                    else:
                        data.append(c)
                    break
                elif(str(c) == ''):
                    #logger.debug ('Timeout')
                    pass
                else:
                    logger.debug(str(c))
                    #c = c.replace('.',',')
                    data.append(c)
            ## END WHILE LOOP

            #logger.debug('>>>Ser: End')
            #logger.debug(data)
            if data != False:
                if (data[0] == 'AT$gpsacp'):
                    del data[0]
                a = data[0].split(',')
                logger.debug(a)
                if a[5] == '0' or a[5] == '1':
                    raise NoGPSLock
        except GPSNotSetup:
            logger.debug("Error: GPS is Not Setup Correctly...Setting Up GPS Default Parmeters")
            data = False
            GpsSetup(ser)
        except NoGPSLock:
            GpsCheckLock()
            logger.debug("Error: No GPS Lock. SatInView = "+str(config.NumSats))
            config.GPSLock = False #Reiterate that there is no GPS Lock
            if config.WaitForGPSLock:
                sleep(2)
                logger.debug('WaitForGPSLock:',config.WaitForGPSLock)

                #Update the LED is there is a change in the #SatsInView
                if config.NumSats != config.lastSatInView:
                    config.lastSatInView = config.NumSats
                    strBlink = str(config.NumSats)
                    SndGPSCmd('AT#SLED=3,'+strBlink+','+strBlink,ser)
                #Recall getGPS to wait for GPS Lock
                getGPS('AT$gpsacp',ser,5,cursor,conn)

        except:
            logger.warning ('Error: Ser Read')

        else:
            #WE HAVE A LOCK!
            logger.debug("<<<GPS LOCK ACQUIRED>>>")
            if config.GPSLock == False:
                SndGPSCmd('AT#SLED=1',ser) #Update the LED!
                config.GPSLock = True #Update the global variable

            gpsSplit = data[0].split(',')
            config.LatestGPS = gpsSplit
            if config.WriteLTEwGPS_to_Sql:
                return gpsSplit
            elif config.WriteGPS_to_Sql: #Only Write it if we are configured for it.
                WriteGPS_to_Sql(gpsSplit,cursor,conn)

    else: logger.critical("Error: Ser Port Not Open")

def GpsCheckLock():
    try:
        ser1 = serial.Serial()
        ser1.baudrate = 115200
        ser1.port = '/dev/ttyUSB1'
        ser1.timeout = 5
        #logger.debug(ser1)
        ser1.open()
        ser1.reset_input_buffer()
        ser1.reset_output_buffer()
        #logger.debug(ser1)
        if(ser1.is_open):
            #logger.debug('>>>Ser1: Read...')
            c = ser1.readline().decode('utf-8').strip()
            logger.debug('[Ser1: GPS] ',c)
            if c=='':
                logger.debug('[Ser1: GPS] ','No Sats in view')
                config.NumSats = 0

            #logger.debug('[Ser1: GPS] ',c)
            c = c.split(',')
            #logger.debug(c)
            #logger.debug(c[3])
            config.NumSats = c[3]
        ser1.close()
    except:
        logger.debug('Error: Cannot Read ser1 @ /dev/ttyUSB1')
        #GpsSetup(config.ser)
        ser1.close()
    finally:
        return config.NumSats



def SndGPSCmd(cmd,ser):
    if(ser.is_open):
        #logger.debug("is_open")
        ser.timeout = 1
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        sleep(0.5)
        output = cmd + '\r'
        ser.write(output.encode())
        sleep(.25)
        #logger.debug('>>>Ser: Read...')
        SerGPS = "[Ser2: GPS] "
        data = []
        try:
            while True:
                c = ser.readline().decode('utf-8').rstrip()
                if ('ended' in str(c)):
                    logger.debug( str(c))
                    break
                elif('ERROR' in str(c)):
                    logger.debug( str(c))
                    return False
                    break
                elif('OK' in str(c)):
                    logger.debug( str(c))
                    return True
                    break
                elif(str(c) == ''):
                    #logger.debug ('Timeout')
                    pass
                else:
                    logger.debug(str(c))
                    #c = c.replace('.',',')
                    data.append(c)
                sleep(0.5)
        except:
            logger.debug ('Error: Ser Read')
            #ser1.close()


        else:
            pass
            #logger.debug('>>>Ser: End')
            #logger.debug(data)

    else: logger.debug("Error: Ser Port Not Open")

def GpsSetup(ser):
    try:
        if (SndGPSCmd('AT$GPSRST',ser)== False):
            raise GPSRST
        elif (SndGPSCmd('AT$GPSNVRAM=15,0',ser)== False):
            raise GPSNVRAM
        elif (SndGPSCmd('AT$GPSNMUN=2,1,0,0,1,0,0',ser)== False):
            raise GPSNMUN
        elif (SndGPSCmd('AT$GPSP=1',ser)== False):
            raise GPSP

    except GPSRST:
        logger.debug("Error: AT$GPSRST Failure")
    except GPSNVRAM:
        logger.debug("Error: AT$GPSNVRAM Failure")
    except GPSNMUN:
        logger.debug("Error: AT$GPSNMUN Failure")
    except GPSP:
        logger.debug("Error: AT$GPSP Failure")

def WriteGPS_to_Sql(values,cursor,conn):
    try:
        mySql_insert_query = """INSERT INTO gps (UTC,latitude,longitude,hdop,altitude,fix,cog,spkm,spkn,date,nsat_gps,nsat_glonass)
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """

        cursor.execute(mySql_insert_query,values)
        conn.commit()
        logger.debug("Sucessfuly Wrote GPS data to server")
    except mysql.connector.Error as error:
        logger.debug("Failed to insert record into MySQL table {}".format(error))
        logger.debug(values)

def setupMySql(cursor,conn):
    logger.debug('setupMySql')
    try:
        #logger.debug(cursor,conn)
        createTable = """CREATE TABLE IF NOT EXISTS gps_status(
                        ID int,
                        time float,
                        lat text,
                        lat_dir char,
                        lng text,
                        lng_dir char,
                        alt float,
                        gpsFix int,
                        satInUse int,
                        satInView int);"""
        truncateTable = "truncate Table gps_status"
        populateTable = """INSERT INTO gps_status (ID, time,lat,lat_dir,lng,lng_dir,alt,gpsFix,satInUse,satInView)
                               VALUES ( %s,     %s,   %s, %s, %s, %s, %s, %s, %s,%s) """
        default_values =                ['1','000.00','0','N','00','W','0','0','0','0']

        #cursor.execute("SHOW TABLES")
        #conn.commit()
        logger.debug("Create Table")
        cursor.execute(createTable)
        sleep(.1)
        logger.debug("TruncateTable")
        sleep(.1)
        cursor.execute(truncateTable)
        conn.commit()

        conn.commit()
        logger.debug("Populate table w default")
        #cursor.execute = (populateTable,default_values)
        cursor.execute(populateTable,default_values)
        conn.commit()
        #cursor.execute = ("select * from gps")
        #conn.commit()
        #logger.debug(cursor.fetchall())
        logger.debug("TableSetup Complete")
    except mysql.connector.Error as error:
        logger.debug("Failed to insert record into MySQL table {}".format(error))
        exit()
    except Exception as e:
        logger.debug(traceback.print_exc())
def main(cursor,conn,ser1):
    try:


        logger.info("GPS_MAIN!")

        setupMySql(cursor,conn)
        while True:
            try:
                logger.debug("whileTrue")
                readGPSstream(cursor,conn,ser1,logger)
                #getGPS('AT$gpsacp',ser2,1,cursor,conn)
                sleep(1)
            except Exception as e:
                logger.info(e)
                #setupMySql(cursor,conn)
                sleep(.5)
    except Exception as e:
        logger.debug(traceback.print_exc())
        conn.close()
        exit()


if __name__ == "__main__":
    conn = config.MySqlconn
    cursor = conn.cursor(buffered=True)
    SerialUSB1 = serial.Serial('/dev/ttyUSB1', 115200, timeout=1)

    main(cursor,conn,SerialUSB1)
