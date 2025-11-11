from gpiozero import PWMOutputDevice, DigitalOutputDevice, DistanceSensor
from gpiozero.pins.lgpio import LGPIOFactory

class Robot:
  def __init__(self):
    # Motor pin mapping
    self.motors = {
      'M1': {'IN1': 24, 'IN2': 23, 'EN': 18},
      'M2': {'IN1': 6, 'IN2': 5, 'EN': 13},
      'M3': {'IN1': 20, 'IN2': 21, 'EN': 19},
      'M4': {'IN1': 16, 'IN2': 26, 'EN': 12},
    }

    self.speed = 0.75

    pin_factory = LGPIOFactory()

    # Setup motor pins
    for _, m in self.motors.items():
      m['L_IN'] = DigitalOutputDevice(m['IN1'], pin_factory=pin_factory)
      m['R_IN'] = DigitalOutputDevice(m['IN2'], pin_factory=pin_factory)
      m['PWM'] = PWMOutputDevice(m['EN'], frequency=1000, pin_factory=pin_factory)

    # Sensor Ping configuration
    self.ping_sensor = None
    self.setup_ping_sensor()

  def setup_ping_sensor(self):
    """
    Setup Parallax Ping 3-pin sensor
    Pin configuration:
    - VCC: 5V
    - GND: Ground
    - SIG: GPIO 17 (Anda bisa mengganti dengan GPIO lain yang tersedia)
    """
    try:
      # Menggunakan GPIO 17 untuk sensor Ping (bisa diganti sesuai kebutuhan)
      self.ping_sensor = DistanceSensor(echo=17, trigger=17, max_distance=3.0, 
                      pin_factory=LGPIOFactory())
      print("Sensor Ping berhasil diinisialisasi")
    except Exception as e:
      print(f"Error inisialisasi sensor Ping: {e}")
      self.ping_sensor = None

  def get_distance(self):
    """
    Mendapatkan jarak dalam centimeter dari sensor Ping
    
    Returns:
      float: Jarak dalam cm, atau -1 jika terjadi error
    """
    if self.ping_sensor is None:
      print("Sensor Ping tidak terinisialisasi")
      return -1
    
    try:
      # gpiozero DistanceSensor mengembalikan jarak dalam meter
      distance_m = self.ping_sensor.distance
      distance_cm = distance_m * 100  # Konversi ke centimeter
      return round(distance_cm, 2)
    except Exception as e:
      print(f"Error membaca sensor: {e}")
      return -1

  def motor_forward(self, motor, speed=0):
    motor['L_IN'].on()
    motor['R_IN'].off()
    motor['PWM'].value = speed if speed != 0 else self.speed

  def motor_backward(self, motor, speed=0):
    motor['L_IN'].off()
    motor['R_IN'].on()
    motor['PWM'].value = speed if speed != 0 else self.speed

  def motor_stop(self, motor):
    motor['L_IN'].off()
    motor['R_IN'].off()
    motor['PWM'].value = 0

  def berhenti(self):
    for motor in self.motors.values():
      self.motor_stop(motor)

  def maju(self, speed=0):
    self.motor_forward(self.motors["M1"], speed)
    self.motor_forward(self.motors["M2"], speed)
    self.motor_forward(self.motors["M3"], speed)
    self.motor_forward(self.motors["M4"], speed)

  def mundur(self, speed=0):
    self.motor_backward(self.motors["M1"], speed)
    self.motor_backward(self.motors["M2"], speed)
    self.motor_backward(self.motors["M3"], speed)
    self.motor_backward(self.motors["M4"], speed)

  def kiri(self, speed=0):
    self.motor_backward(self.motors["M1"], speed)
    self.motor_forward(self.motors["M2"], speed)
    self.motor_backward(self.motors["M3"], speed * 0.5)
    self.motor_forward(self.motors["M4"], speed)

  def kanan(self, speed=0):
    self.motor_forward(self.motors["M1"], speed)
    self.motor_backward(self.motors["M2"], speed)
    self.motor_forward(self.motors["M3"], speed)
    self.motor_backward(self.motors["M4"], speed * 0.5)

  def mundur_kiri(self, speed=0):
    self.motor_forward(self.motors["M1"], speed * 0.5)
    self.motor_backward(self.motors["M2"], speed)
    self.motor_forward(self.motors["M3"], speed)
    self.motor_backward(self.motors["M4"], speed)

  def mundur_kanan(self, speed=0):
    self.motor_backward(self.motors["M1"], speed)
    self.motor_forward(self.motors["M2"], speed * 0.5)
    self.motor_backward(self.motors["M3"], speed)
    self.motor_forward(self.motors["M4"], speed)

  def putar_kiri(self, speed=0):
    self.motor_forward(self.motors["M1"], speed)
    self.motor_backward(self.motors["M2"], speed)
    self.motor_forward(self.motors["M3"], speed)
    self.motor_backward(self.motors["M4"], speed)

  def putar_kanan(self, speed=0):
    self.motor_backward(self.motors["M1"], speed)
    self.motor_forward(self.motors["M2"], speed)
    self.motor_backward(self.motors["M3"], speed)
    self.motor_forward(self.motors["M4"], speed)
