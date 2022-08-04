from time import sleep

import serial
import mysql.connector

#local Modules
import sys
import config
from ErrorLogging import *
LogHed_GPS = config.LogHed_GPS

def getGPS(cmd,ser,timeout,cursor,conn):
    LogHed_GPS = config.LogHed_GPS
    if(ser.is_open):
        #print(LogHed_GPS,"is_open")
        ser.timeout = timeout
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        sleep(0.5)
        output = cmd + '\r'
        ser.write(output.encode())
        sleep(.25)
        #print(LogHed_GPS,'>>>Ser: Read...')
        SerGPS = "[Ser2: GPS] "
        data = []
        try:
            while True:
                c = ser.readline().decode('utf-8').rstrip()
                if ('ended' in str(c)):
                    print(SerGPS, str(c))
                    break
                elif('ERROR' in str(c)):
                    print(SerGPS, str(c))
                    break
                elif('OK' in str(c)):
                    print(SerGPS, str(c))
                    break
                elif('$GPSACP:' in str(c)):
                    print(SerGPS, str(c))
                    c = c.removeprefix('$GPSACP:')
                    if c == '':
                        raise GPSNotSetup
                    else:
                        data.append(c)
                    break
                elif(str(c) == ''):
                    #print ('Timeout')
                    pass
                else:
                    print(SerGPS, str(c))
                    #c = c.replace('.',',')
                    data.append(c)
            ## END WHILE LOOP

            #print(LogHed_GPS,'>>>Ser: End')
            #print(LogHed_GPS,data)
            if data != False:
                if (data[0] == 'AT$gpsacp'):
                    del data[0]
                a = data[0].split(',')
                print(a)
                if a[5] == '0' or a[5] == '1':
                    raise NoGPSLock
        except GPSNotSetup:
            print(LogHed_GPS,"Error: GPS is Not Setup Correctly...Setting Up GPS Default Parmeters")
            data = False
            GpsSetup(ser)
        except NoGPSLock:
            GpsCheckLock()
            print(LogHed_GPS,"Error: No GPS Lock. SatInView = "+str(config.NumSats))
            config.GPSLock = False #Reiterate that there is no GPS Lock
            if config.WaitForGPSLock:
                sleep(2)
                print(LogHed_GPS,'WaitForGPSLock:',config.WaitForGPSLock)

                #Update the LED is there is a change in the #SatsInView
                if config.NumSats != config.lastSatInView:
                    config.lastSatInView = config.NumSats
                    strBlink = str(config.NumSats)
                    SndGPSCmd('AT#SLED=3,'+strBlink+','+strBlink,ser)
                #Recall getGPS to wait for GPS Lock
                getGPS('AT$gpsacp',ser,5,cursor,conn)

        except:
            print ('Error: Ser Read')

        else:
            #WE HAVE A LOCK!
            print(LogHed_GPS,"<<<GPS LOCK ACQUIRED>>>")
            if config.GPSLock == False:
                SndGPSCmd('AT#SLED=1',ser) #Update the LED!
                config.GPSLock = True #Update the global variable

            gpsSplit = data[0].split(',')
            config.LatestGPS = gpsSplit
            if config.WriteLTEwGPS_to_Sql:
                return gpsSplit
            elif config.WriteGPS_to_Sql: #Only Write it if we are configured for it.
                WriteGPS_to_Sql(gpsSplit,cursor,conn)

    else: print(LogHed_GPS,"Error: Ser Port Not Open")

def GpsCheckLock():
    try:
        ser1 = serial.Serial()
        ser1.baudrate = 115200
        ser1.port = '/dev/ttyUSB1'
        ser1.timeout = 5
        #print(LogHed_GPS,ser1)
        ser1.open()
        ser1.reset_input_buffer()
        ser1.reset_output_buffer()
        #print(ser1)
        if(ser1.is_open):
            #print('>>>Ser1: Read...')
            c = ser1.readline().decode('utf-8').strip()
            print('[Ser1: GPS] ',c)
            if c=='':
                print('[Ser1: GPS] ','No Sats in view')
                config.NumSats = 0

            #print('[Ser1: GPS] ',c)
            c = c.split(',')
            #print(LogHed_GPS,c)
            #print(LogHed_GPS,c[3])
            config.NumSats = c[3]
        ser1.close()
    except:
        print(LogHed_GPS,'Error: Cannot Read ser1 @ /dev/ttyUSB1')
        #GpsSetup(config.ser)
        ser1.close()
    finally:
        return config.NumSats

def SndGPSCmd(cmd,ser):
    if(ser.is_open):
        #print(LogHed_GPS,"is_open")
        ser.timeout = 1
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        sleep(0.5)
        output = cmd + '\r'
        ser.write(output.encode())
        sleep(.25)
        #print(LogHed_GPS,'>>>Ser: Read...')
        SerGPS = "[Ser2: GPS] "
        data = []
        try:
            while True:
                c = ser.readline().decode('utf-8').rstrip()
                if ('ended' in str(c)):
                    print(SerGPS, str(c))
                    break
                elif('ERROR' in str(c)):
                    print(SerGPS, str(c))
                    return False
                    break
                elif('OK' in str(c)):
                    print(SerGPS, str(c))
                    return True
                    break
                elif(str(c) == ''):
                    #print ('Timeout')
                    pass
                else:
                    print(SerGPS, str(c))
                    #c = c.replace('.',',')
                    data.append(c)
                sleep(0.5)
        except:
            print ('Error: Ser Read')
            ser1.close()


        else:
            pass
            #print(LogHed_GPS,'>>>Ser: End')
            #print(LogHed_GPS,data)

    else: print(LogHed_GPS,"Error: Ser Port Not Open")

def GpsSetup(ser):
    try:
        if (SndGPSCmd('AT$GPSRST',ser)== False):
            raise GPSRST
        elif (SndGPSCmd('AT$GPSNVRAM=15,0',ser)== False):
            raise GPSNVRAM
        elif (SndGPSCmd('AT$GPSNMUN=2,0,0,0,1,0,0',ser)== False):
            raise GPSNMUN
        elif (SndGPSCmd('AT$GPSP=1',ser)== False):
            raise GPSP

    except GPSRST:
        print(LogHed_GPS,"Error: AT$GPSRST Failure")
    except GPSNVRAM:
        print(LogHed_GPS,"Error: AT$GPSNVRAM Failure")
    except GPSNMUN:
        print(LogHed_GPS,"Error: AT$GPSNMUN Failure")
    except GPSP:
        print(LogHed_GPS,"Error: AT$GPSP Failure")

def WriteGPS_to_Sql(values,cursor,conn):
    try:
        mySql_insert_query = """INSERT INTO gps (UTC,latitude,longitude,hdop,altitude,fix,cog,spkm,spkn,date,nsat_gps,nsat_glonass)
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """

        cursor.execute(mySql_insert_query,values)
        conn.commit()
        print(LogHed_GPS,"Sucessfuly Wrote GPS data to server")
    except mysql.connector.Error as error:
        print(LogHed_GPS,"Failed to insert record into MySQL table {}".format(error))
        print(LogHed_GPS,values)
