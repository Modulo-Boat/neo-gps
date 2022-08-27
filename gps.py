import io
import pynmea2
import redis
import serial
import threading

from datetime import datetime, timedelta
from metrics import Metrics

class Gps():
  def __init__(self, port='/dev/ttyUSB1'):
    ser=serial.Serial(port, baudrate=38400,bytesize=8, parity='N', stopbits=1,timeout=0.5)
    self.sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))

    self.latitude = None
    self.lat_dir = None
    self.longitude = None
    self.lon_dir = None
    self.altitude = None
    self.alt_unit = None
    self.speed = None
    self.true_course = None
    self._redis = redis.Redis(host='192.168.1.123', port=30002)
    self._metric = Metrics()

    execute_thread = threading.Thread(target=self.execute)
    execute_thread.start()

  def update(self, var, val):
    if var == "latitude":
      self._redis.publish('gps_latitude', val)
      self._metric.update_latitude(val)
    elif var == "lat_dir":
      self._redis.publish('gps_lat_dir', val)
    elif var == "longitude":
      self._redis.publish('gps_longitude', val)
      self._metric.update_longitude(val)
    elif var == "lon_dir":
      self._redis.publish('gps_lon_dir', val)
    elif var == 'altitude':
      self._redis.publish('gps_altitude', val)
      self._metric.update_altitude(val)
    elif var == 'alt_unit':
      self._redis.publish('gps_alt_unit', val)
    elif var == 'speed':
      self._redis.publish('gps_speed', val)
      self._metric.update_speed(val)
    elif var == 'true_course':
      self._redis.publish('gps_true_course', val)
      self._metric.update_true_course(val)

  def execute(self):
    while True:
      try:
        line = self.sio.readline()
        msg = pynmea2.parse(line)
        NMEAsen = str(msg)
        #look for GNGGA and GNVTG sentences; these have the info we want (use pynmea2 and string parsing), otherwise continue
        # GGA = Global Positioning System Fix Data
        if NMEAsen[0:6]=="$GNGGA":
          splitsen = NMEAsen.split(",")
          print(splitsen)
          self.altitude = msg.altitude
          self.alt_unit = msg.altitude_units
          gps="Altitude1: " + str(self.altitude) + str(self.alt_unit)
          print(gps)
          print()

        # RMC = Recommended Minimum Specific GNSS Data
        elif NMEAsen[0:6]=="$GNRMC":
          splitsen = NMEAsen.split(",")
          print(splitsen)
          #self.latitude = msg.latitude
          self.update('latitude', msg.latitude)
          #self.lat_dir = msg.lat_dir
          self.update('lat_dir', msg.lat_dir)
          #self.longitude = msg.longitude
          self.update('longitude', msg.longitude)
          #self.lon_dir = msg.lon_dir
          self.update('lon_dir', msg.lon_dir)
          #self.speed = round(float (splitsen[7]) *1.852,3)
          self.update('speed', round(float (splitsen[7]) *1.852,3))
          #self.true_course = msg.true_course
          self.update('true_course', msg.true_course)
          gps=  "Latitsude: " + str(self.latitude)+ str(self.lat_dir) \
            + " and Longitude: " + str(self.longitude)+ str(self.lon_dir) \
            + " and true_course: " + str(self.true_course) \
            + " and speed: " + str(self.speed) + "km/h" 
          
          print(gps)
          print("gnrmc")

        # VTG = Course Over Ground and Ground Speed
        elif NMEAsen[0:6]=="$GNVTG":
          splitsen = NMEAsen.split(",")
          speed = msg.spd_over_grnd_kmph
        else:
          continue
      except KeyboardInterrupt:
        print('exit')
        break
      except:
        print(" ")

if __name__ == '__main__':
  Gps()