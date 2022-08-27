import prometheus_client

class Metrics:
  def __init__(self, interval_seconds=0):   
    self.latitude = prometheus_client.Gauge("gps_latitude", "Latitude")
    self.longitude = prometheus_client.Gauge("gps_longitude", "Longitude")
    self.altitude = prometheus_client.Gauge("gps_altitude", "Altitude")
    self.speed = prometheus_client.Gauge("gps_Speed", "Speed")
    self.true_course = prometheus_client.Gauge("gps_true_course", "True Course")
    prometheus_client.start_http_server(9090)

  def update_latitude(self, number):
    self.latitude.set(number)
    print('latitude', number)

  def update_longitude(self, number):
    self.longitude.set(number)
    print('longitude', number)

  def update_altitude(self, number):
    self.altitude.set(number)
    print('altitude', number)

  def update_speed(self, number):
    self.speed.set(number)

  def update_true_course(self, number):
    self.true_course.set(number)