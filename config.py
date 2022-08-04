import serial
import mysql.connector


## Configurations
WaitForGPSLock = True
WriteGPS_to_Sql = False
WriteLTE_to_Sql = False
WriteLTEwGPS_to_Sql = True
MainLoopTimer = 2

## Global References
GPSLock = False
lastSatInView = 0
NumSats = 0
LatestGPS = ['015527.000','4008.4342N','07532.2191W','500.0','1296.5','2','291.1','11.3','6.1','031221','03','00']
ser = False
LogHed_LTESearch_USB   = "[Main: USB]"
LogHed_LTESearch_MySql = "[Main: Sql]"
LogHed_LTESearch_Sys   = "[Main: SYS]"

LogHed_LTE = "[LTE: ]"
LogHed_GPS = "[GPS: ]"


MySqlconn = mysql.connector.connect(host='localhost',
                               database='LTE_Cells',
                               user='admin',
                               password='admin',
                               )
