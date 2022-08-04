from time import sleep
###Local Modules
import sys
import config
from GPS import *
WriteLTEwGPS_to_Sql = config.WriteLTEwGPS_to_Sql
LogHed_LTE = config.LogHed_LTE
WriteLTE_to_Sql = config.WriteLTE_to_Sql
CellsInView = [['4384', '-59', '310', '410', '1696', '142683884', '2953', '0', '-64', '-5', '0'],
                ['9799', '-61', '310', '260', '7456', '53022122', '34692', '0', '-68', '-8', '5'],
                ['5110', '-43', '310', '410', '5427472', '267', '358', '0', '-74', '-14', '10'],
                ['5035', '-50', '310', '260', '35050757', '22036', '312', '0', '-84', '-20', '5'],
                ['5230', '-47', '311', '480', '25933058', '26375', '403', '0', '-76', '-12', '10'],
                ['66986', '-103', '310', '410', '5427643', '267', '358', '4', '-140', '-20', '10'],
                ['5230', '-42', '311', '480', '25933058', '26375', '403', '0', '-79', '-20', '10'],
                ['5035', '-49', '310','260', '35050757', '22036', '312', '0', '-83', '-20', '5'],
                ['5110', '-46', '310', '410', '5427472','267', '358', '0', '-75', '-12', '10'],
                ['1125', '-47', '310', '260', '12539400', '22036', '78', '0', '-86', '-20', '15'],
                ['2560', '-50', '311', '480', '25933083', '26375', '403', '0', '-79', '-12', '10'],
                ['1000', '-63', '311', '480', '25933070', '26375', '402', '0', '-92', '-12', '10'],
                ['2000', '-50', '310', '410', '5427479', '267', '358', '0', '-78', '-11', '10'],
                ['2300', '-45', '310', '260', '12539394', '22036', '320', '0', '-85', '-20', '20'],
                ['5330', '-49', '310', '410', '5427650', '267', '358', '0', '-74', '-8', '10'],
                ['700', '-46', '310', '410', '5427465', '267', '358', '0', '-78', '-12', '20'],
                ['2125', '-60', '311', '480', '25933068', '26375', '402', '0', '-89', '-10', '15'],
                ['66986', '-103', '310', '410', '5427643', '267', '358', '4', '-140', '-20', '10'],
                ['67086', '-70', '311','480', '25933074', '26375', '402', '0', '-98', '-11', '10'],
                ['68661', '-40', '310', '260', '35050814', '22036', '234', '0', '-74', '-20', '5']]

def getCells(cmd,ser,timeout,cursor,conn):
    if(ser.is_open):
        #print(LogHed_LTE,"is_open")
        ser.timeout = timeout
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        sleep(0.5)
        output = cmd + '\r'
        ser.write(output.encode())
        sleep(.25)
        #print(LogHed_LTE,'>>>Ser: Read...')
        SerLTE = "[Ser2: LTE] "
        data = []
        try:
            while True:
                try:
                    c = ser.readline().decode('utf-8').rstrip()
                    if ('ended' in str(c)):
                        print(SerLTE,str(c))
                        break
                    elif('ERROR' in str(c)):
                        raise NetworkSurveyError
                        print(SerLTE,str(c))
                        break
                    elif('OK' in str(c)):
                        print(SerLTE,str(c))
                        break
                    elif(str(c) == ''):
                        #print ('Timeout')
                        pass
                    else:
                        print(SerLTE,str(c))
                        c = c.replace('.',',')
                        data.append(c)
                except NetworkSurveyError:
                    print(LogHed_LTE,"Error: Network Survey Error")
                    break
        except:
            print ('Error: Ser Read')
        #print(LogHed_LTE,'>>>Ser: End')

        try:
            #clean the LTE data from serial
            data = cleanCellOutput(data)
            CellsInView = data
            print(data)
            #Check How we are going to write out data to the server
            if   WriteLTEwGPS_to_Sql == False and WriteLTE_to_Sql == True:
                WriteCells_to_Sql(data,cursor,conn,ser)
            elif WriteLTEwGPS_to_Sql == True and WriteLTE_to_Sql == False:
                print(LogHed_LTE,"Getting most current GPS location...")
                GPSdata = getGPS('AT$gpsacp',ser,5,cursor,conn)
                GPSdata = [x.strip(' ') for x in GPSdata]
                WriteCellswGPS_to_Sql(data,GPSdata,cursor,conn,ser)
            elif WriteLTEwGPS_to_Sql == True and WriteLTE_to_Sql == True:
                #WriteCells_to_Sql(data,cursor,conn)
                pass
            elif WriteLTEwGPS_to_Sql == False and WriteLTE_to_Sql == False:
                pass
        except:
            print(LogHed_LTE,"Error writing LTE Data to Server")


    else: print(LogHed_LTE,"Error: Ser Port Not Open")


def WriteCells_to_Sql(values,cursor,conn,ser):
    try:
        mySql_insert_query = """INSERT INTO cells (earfcn,rxLev,mcc,mnc,cellId,tac,pci,cellStatus,rsrp,rsrq,bandwidth)
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """

        #values = ["4384,-65,310,410,1696,142683884,2953,0,-67,-6,5",
        #          "66986,-103,310,410,142683884,410,0166,4,-140,-20,10"]
        if conn.is_connected():
            #print(LogHed_LTE,'Connected to MySQL database')
            for i in values:
                a = i.split(",")
                if len(a) == 10:
                    a.append('0')
                #print(LogHed_LTE,a)
                cursor.execute(mySql_insert_query,a)
        #cursor.executemany(mySql_insert_query, values)
            conn.commit()
            print(LogHed_LTE,'Successfully Wrote LTE data to cells')
        #print(LogHed_LTE,cursor.rowcount, "Record inserted successfully into Laptop table")

    except mysql.connector.Error as error:
        print(LogHed_LTE,"Failed to insert record into MySQL table {}".format(error))
        print(LogHed_LTE,i)

def WriteCellswGPS_to_Sql(LTEvalues,GPSvalues,cursor,conn,ser):
    try:
        mySql_insert_query = """INSERT INTO LTEwGPS (earfcn,rxLev,mcc,mnc,cellId,tac,pci,cellStatus,rsrp,rsrq,bandwidth,UTC,latitude,longitude,hdop,altitude,fix,cog,spkm,spkn,date,nsat_gps,nsat_glonass)
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s ) """

        #values = ["4384,-65,310,410,1696,142683884,2953,0,-67,-6,5",
        #          "66986,-103,310,410,142683884,410,0166,4,-140,-20,10"]
        if conn.is_connected():
            print(LogHed_LTE,'Connected to MySQL database')
        print(LogHed_LTE,"Writing Cell Data w/ GPS to LTEwGPS")
        for i in LTEvalues:
            #print(LogHed_LTE,i)
            i.extend(GPSvalues)
            #print(LogHed_LTE,i)
            cursor.execute(mySql_insert_query,i)
        conn.commit()
        print(LogHed_LTE,'Successfully Wrote LTE data to LTEwGPS')
        #print(LogHed_LTE,cursor.rowcount, "Record inserted successfully into Laptop table")

    except mysql.connector.Error as error:
        print(LogHed_LTE,"Failed to insert record into MySQL table {}".format(error))
        print(LogHed_LTE,i,GPSvalues)
        CheckSurveyFormat()

def CheckSurveyFormat():
        #check NetworkSurveyFormat 0 = decimal format
    try:
        #print(LogHed_LTE,"Checking ")
        data = SndLTECmd('AT#CSURVF?',ser)
        print(LogHed_LTE,data)
        print(LogHed_LTE,data[1])
        if data[1] != '0':
            SndLTECmd('AT#CSURVF=0',ser)
    except:
        print(LogHed_LTE,'CheckSurveyFormat: Unable to send/read AT command(s)')


def SndLTECmd(cmd,ser):
    if(ser.is_open):
        #print(LogHed_LTE,"is_open")
        ser.timeout = 1
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        sleep(0.5)
        output = cmd + '\r'
        ser.write(output.encode())
        sleep(.25)
        #print(LogHed_LTE,'>>>Ser: Read...')
        SerLTE = "[Ser2: LTE] "
        data = []
        try:
            while True:
                c = ser.readline().decode('utf-8').rstrip()
                if ('ended' in str(c)):
                    print(SerGPS, str(c))
                    break
                elif('ERROR' in str(c)):
                    print(SerLTE, str(c))
                    return False
                    break
                elif('OK' in str(c)):
                    print(SerLTE, str(c))
                    return True
                    break
                elif(str(c) == ''):
                    #print ('Timeout')
                    pass
                else:
                    print(SerLTE, str(c))
                    #c = c.replace('.',',')
                    data.append(c)
        except:
            print ('Error: Ser Read')

        finally:
            return data
            #print(LogHed_LTE,'>>>Ser: End')
            #print(LogHed_LTE,data)

    else: print(LogHed_LTE,"Error: Ser Port Not Open")



def cleanCellOutput(values):
    data = []
    for i in range(0,len(values)-1):
        if('AT#' in str(values[i])):
            del values[i]
            break
    for i in range(0,len(values)-1):
        if('Network' in str(values[i])):
            del values[i]
            break
    for i in values:
        a = i.split(",")
        if len(a) == 10:
            a.append('0')
        data.append(a)
    return data
