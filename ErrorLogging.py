# define Python user-defined exceptions

#Local Modules
import sys
import config
class Error(Exception):
    """Base class for other exceptions"""
    pass


class NetworkSurveyError(Error):
    """Raised when the CSURV(Cell Survey) returns an error"""
    pass


class GPSNotSetup(Error):
    """Raised when GPS returns OK and is not setup"""
    pass

class GPSRST(Error):
    """Raised when AT$GPSRST (Reset) fails"""
    pass

class GPSNVRAM(Error):
    """Raised when error in Deleling the GPS information stored in NVM"""
    pass
class GPSNMUN(Error):
    """Raised when For enabling unsolicited messages of GNSS data in NMEA format, all sentence is enabled"""
    pass

class GPSP(Error):
    """Raised when error starting GPSP in standalone mode"""
    pass
class NoGPSLock(Error):
    """Raised when there is no GSP Lock available"""
    pass
