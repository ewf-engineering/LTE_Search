#!/usr/bin/env python3
from time import sleep
import datetime
import traceback
import serial
import mysql.connector
import logging
#local Modules
import sys
import config

from ErrorLogging import *
LogHed_LTE = config.LogHed_LTE

#AT#CSURVF=0

logger = logging.getLogger('LTE')
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

def setupMySql(cursor,conn):
    logger.debug('setupMySql')
    try:
        #logger.debug(cursor,conn)
        createTable = """CREATE TABLE IF NOT EXISTS cells(
                        earfcn int,
                        rxLev int,
                        mcc int,
                        mnc int,
                        cellId int,
                        tac int,
                        pci int,
                        cellStatus int,
                        rsrp int,
                        rsrq int,
                        bandwidth int
                        );"""
        dropTable = "Truncate Table cells"
        populateTable = """INSERT INTO cells (earfcn,rxLev,mcc,mnc,cellId,tac,pci,cellStatus,rsrp,rsrq,bandwidth)
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """
        default_values =                ['1','000.00','0','N','00','W','0','0','0','0']
        #cursor.execute("SHOW TABLES")
        #conn.commit()

        #logger.debug("DropTable")
        sleep(.1)
        cursor.execute(dropTable)
        conn.commit()
        cursor.execute(createTable)
        conn.commit()
        #logger.debug('create_Table')
        #cursor.execute = (populateTable,default_values)
        #cursor.execute(populateTable,default_values)
        #conn.commit()
        #logger.debug('getStatus')
        #cursor.execute = ("select * from gps")
        #conn.commit()
        #logger.debug(cursor.fetchall())
        #logger.debug("MakeTable")
    except mysql.connector.Error as error:
        logger.debug("Failed to insert record into MySQL table {}".format(error))
        exit()
    except Exception as e:
        traceback.print_exc()

def checkFormat(ser):
    try:
        if ser.is_open:
            ser.timeout = 1
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            sleep(0.5)
            cmd = "AT#CSURVF?"
            output = cmd + '\r'
            ser.write(output.encode())
            sleep(.25)
            SerLTE = "[Ser2: LTE] "
            value = 0
            data = []
            try:
                loop = 0
                loopBreak = 20*1 #5*20 = 100s. We run away after ~2 min of nothingness.
                while True:
                    try:
                        c = ser.readline().decode('utf-8').rstrip().strip(',')
                        if('ERROR' in str(c)):
                            raise NetworkSurveyError
                            logger.debug(str(c))
                            break
                        elif('OK' in str(c)):
                            logger.debug(str(c))
                            break
                        elif(str(c) == ''):
                            #print ('.',end='')
                            loop += 1 #Nothingness
                        elif loop == loopBreak:
                            break
                        else:
                            logger.debug(str(c))
                            c = c.replace('.',',')
                            try:
                                if int(c):
                                    value = c
                            except:
                                pass
                    except NetworkSurveyError:
                        logger.debug("Error: Network Survey Error")
            except Exception as e:
                traceback.print_exc()
            if value != 0:
                cmd = "AT#CSURVF=0"
                output = cmd + '\r'
                ser.write(output.encode())
                while True:
                    try:
                        c = ser.readline().decode('utf-8').rstrip().strip(',')
                        if('ERROR' in str(c)):
                            raise NetworkSurveyError
                            logger.debug(str(c))
                            break
                        elif('OK' in str(c)):
                            logger.debug(str(c))
                            break
                        elif(str(c) == ''):
                            #print ('.',end='')
                            loop += 1 #Nothingness
                        elif loop == loopBreak:
                            break
                        else:
                            logger.debug(str(c))
                            c = c.replace('.',',')
                            try:
                                if int(c):
                                    value = c
                            except:
                                pass
                    except NetworkSurveyError:
                        logger.debug("Error: Network Survey Error")

    except Exception as e:
        traceback.print_exc()

def getCells(cmd,ser,timeout,cursor,conn):
    if(ser.is_open):
        #logger.debug("is_open")
        ser.timeout = timeout
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        sleep(0.5)
        output = cmd + '\r'
        ser.write(output.encode())
        sleep(.25)
        #logger.debug('>>>Ser: Read...')
        SerLTE = "[Ser2: LTE] "
        data = []
        try:
            loop = 0
            loopBreak = 20*timeout #5*20 = 100s. We run away after ~2 min of nothingness.
            while True:
                try:
                    #logger.debug(loop)

                    c = ser.readline().decode('utf-8').rstrip().strip(',')
                    #if ('ended' in str(c)):
                    #    logger.debug(str(c))
                    #    break
                    if('ERROR' in str(c)):
                        raise NetworkSurveyError
                        logger.debug(str(c))
                        break
                    elif('OK' in str(c)):
                        logger.debug(str(c))
                        break
                    elif(str(c) == ''):
                        #print ('.',end='')
                        loop += 1 #Nothingness
                    elif loop == loopBreak:
                        break
                    else:
                        logger.debug(str(c))
                        c = c.replace('.',',')
                        c.strip(',')
                        #logger.debug(c[0])
                        try:
                            if int(c[0]): #we're only looking for integers not txt here:
                                data.append(c)
                        except:
                            pass
                        loop = 0; #reset the looptime cuz we got something

                except NetworkSurveyError:
                    logger.debug("Error: Network Survey Error")
                    break
            #whileTrue (Done reading from the CMD)
            #logger.debug(data)
            logger.debug("Network Data: %s",len(data))
            if len(data) != 0: #if (list) will return true if there is something in there
                logger.debug("WriteToCells")
                WriteToCells(data,cursor,conn)
            if len(data) !=0 and checkGPSLock(cursor,conn):
                logger.debug("writeCells_w_GPS")
                writeCells_w_GPS(data,cursor,conn)
                pass
            sleep(1)
        except Exception as e:
            print ('Error: Ser Read',e)
            logger.debug(traceback.print_exc())
            #logger.debug('>>>Ser: End')

def checkGPSLock(cursor,conn):
    try:
        logger.debug("Checking GPS Lock")
        sql_query = "SELECT gpsFix from gps_status where ID=1;"
        logger.debug("conn_is_conn: %s",conn.is_connected())
        if conn.is_connected():
            logger.debug(conn.is_connected())
            cursor.execute(sql_query)
            conn.commit()
            value = str(cursor.fetchall()).strip("()[],")
            logger.debug("GPS Lock = %s",value);
            if value == "1":
                #logger.debug("TRUE")
                return True
            else:
                return False
    except Exception as e:
        logger.warning("checkGPSLock %s" , e)

def getGPSvalues(cursor,conn):
    try:
        logger.debug("getting GPS Info")
        sql_query = "SELECT * from gps_status where ID=1;"
        if conn.is_connected():
            cursor.execute(sql_query)
            conn.commit()
            value = str(cursor.fetchall()).strip("[]()''""").split(',')
            logger.debug("All GPS Values: %s",value[1]);
            data = [value[1].strip(),value[2].strip().replace("'",""),value[3].strip().replace("'",""),value[4].strip().replace("'",""),value[5].strip().replace("'",""),value[6].strip()]
            logger.debug("GPS Values %s", data)
            return data
    except Exception as e:
        logger.warning("checkGPSLock" + e)

def writeCells_w_GPS(values,cursor,conn):
    try:
        logger.debug("Writing Cell_w_GPS")
        date = datetime.date.today().strftime("%d_%m_%y")
        logger.debug(date)
        createTable = """CREATE TABLE IF NOT EXISTS """ +str(date) + """(
                     time float,
                     earfcn int,
                     rxLev int,
                     mcc int,
                     mnc int,
                     cellId int,
                     tac int,
                     pci int,
                     cellStatus int,
                     rsrp int,
                     rsrq int,
                     bandwidth int,
                     lat text,
                     lat_dir char,
                     lng text,
                     lng_dir char,
                     alt float );"""
        logger.debug(createTable)
        mySql_insert_query = """INSERT INTO """ +str(date) + """ (time,earfcn,rxLev,mcc,mnc,cellId,tac,pci,cellStatus,rsrp,rsrq,bandwidth,lat,lat_dir,lng,lng_dir,alt)
                               VALUES (%s,%s,%s,%s,%s,%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """
        gps = getGPSvalues(cursor,conn)
        #values = ["4384,-65,310,410,1696,142683884,2953,0,-67,-6,5",
        #          "66986,-103,310,410,142683884,410,0166,4,-140,-20,10"]
        if conn.is_connected():
            #logger.debug('Connected to MySQL database')
        #print ("TRUNCATE TABLE cells")
            cursor.execute(createTable)
            conn.commit()
            #logger.debug("Writing to cells")
            for i in values:
                a = i.split(",")
                if len(a) == 10:
                    a.append('0')
                for x in range(0,len(gps)):
                    if x ==0:
                        a.insert(0,gps[x])
                    else:
                        a.append(gps[x])
                logger.debug(a)
                cursor.execute(mySql_insert_query,a)
            conn.commit()
            logger.debug('Successfully Wrote LTE data to %s',date)
        #logger.debug(cursor.rowcount, "Record inserted successfully into Laptop table")

    except mysql.connector.Error as error:
        logger.debug("Failed to insert record into MySQL table {}".format(error))
        logger.debug(a)
        logger.debug(error)
        if ('tac' in error):
            checkFormat(ser2)
        #CheckSurveyFormat()


def WriteToCells(values,cursor,conn):
    try:
        logger.debug("Writting to Cells")
        mySql_insert_query = """INSERT INTO cells (earfcn,rxLev,mcc,mnc,cellId,tac,pci,cellStatus,rsrp,rsrq,bandwidth)
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """

        #values = ["4384,-65,310,410,1696,142683884,2953,0,-67,-6,5",
        #          "66986,-103,310,410,142683884,410,0166,4,-140,-20,10"]
        if conn.is_connected():
            #logger.debug('Connected to MySQL database')
        #print ("TRUNCATE TABLE cells")
            cursor.execute("TRUNCATE TABLE cells")
            conn.commit()
            #logger.debug("Writing to cells")
            for i in values:
                a = i.split(",")
                if len(a) == 10:
                    a.append('0')
                cursor.execute(mySql_insert_query,a)
            conn.commit()
            logger.debug('Successfully Wrote LTE data to cells')
        #logger.debug(cursor.rowcount, "Record inserted successfully into Laptop table")

    except mysql.connector.Error as error:
        logger.debug("Failed to insert record into MySQL table {}".format(error))
        logger.debug(i)
        logger.debug(error)
        if ('tac' in error):
            checkFormat(ser2)
        #CheckSurveyFormat()


def main(cursor,conn,ser2):
    try:
        logger.debug("LTE_MAIN!")


        setupMySql(cursor,conn)
        checkFormat(ser2)
        #getGPSvalues(cursor,conn)
        #checkGPSLock(cursor,conn)
        #exit()
        while True:
            #logger.debug("whileTrue")
            getCells("AT#CSURVC",ser2,5,cursor,conn)
            #getGPS('AT$gpsacp',ser2,1,cursor,conn)
            sleep(1)

    except Exception as e:
        traceback.print_exc()
        #conn.close()
        exit()


if __name__ == "__main__":
    conn = config.MySqlconn
    cursor = conn.cursor(buffered=True)
    SerialUSB2 = serial.Serial('/dev/ttyUSB2', 115200, timeout=1)

    main(cursor,conn,SerialUSB2)
