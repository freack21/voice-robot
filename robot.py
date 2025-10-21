from gpiozero import PWMOutputDevice, DigitalOutputDevice
from gpiozero.pins.lgpio import LGPIOFactory

class Robot :
  def __init__(self) :
    # Motor pin mapping
    self.motors = {
      'M1': {'IN1': 24, 'IN2': 23, 'EN': 18},
      'M2': {'IN1': 16, 'IN2': 26, 'EN': 12},
      'M3': {'IN1': 6, 'IN2': 5, 'EN': 13},
      'M4': {'IN1': 20, 'IN2': 21, 'EN': 19},
    }

    self.speed = 0.75

    pin_factory = LGPIOFactory()

    # Setup motor pins
    for _, m in self.motors.items():
      m['L_IN'] = DigitalOutputDevice(m['IN1'], pin_factory=pin_factory)
      m['R_IN'] = DigitalOutputDevice(m['IN2'], pin_factory=pin_factory)
      m['PWM'] = PWMOutputDevice(m['EN'], frequency=1000, pin_factory=pin_factory)


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


  # ++++++++++++++
  def berhenti(self):
    self.motor_stop(self.motors["M1"])
    self.motor_stop(self.motors["M2"])
    self.motor_stop(self.motors["M3"])
    self.motor_stop(self.motors["M4"])

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
    self.motor_backward(self.motors["M1"], speed * 0.5)
    self.motor_forward(self.motors["M2"], speed)
    self.motor_forward(self.motors["M3"], speed)
    self.motor_forward(self.motors["M4"], speed)

  def kanan(self, speed=0):
    self.motor_forward(self.motors["M1"], speed)
    self.motor_backward(self.motors["M2"], speed * 0.5)
    self.motor_forward(self.motors["M3"], speed)
    self.motor_forward(self.motors["M4"], speed)

  def mundur_kiri(self, speed=0):
    self.motor_backward(self.motors["M1"], speed)
    self.motor_backward(self.motors["M2"], speed)
    self.motor_forward(self.motors["M3"], speed * 0.5)
    self.motor_backward(self.motors["M4"], speed)

  def mundur_kanan(self, speed=0):
    self.motor_backward(self.motors["M1"], speed)
    self.motor_backward(self.motors["M2"], speed)
    self.motor_backward(self.motors["M3"], speed)
    self.motor_forward(self.motors["M4"], speed * 0.5)

  def putar_kiri(self, speed=0):
    self.motor_backward(self.motors["M1"], speed)
    self.motor_forward(self.motors["M2"], speed)
    self.motor_backward(self.motors["M3"], speed)
    self.motor_forward(self.motors["M4"], speed)

  def putar_kanan(self, speed=0):
    self.motor_forward(self.motors["M1"], speed)
    self.motor_backward(self.motors["M2"], speed)
    self.motor_forward(self.motors["M3"], speed)
    self.motor_backward(self.motors["M4"], speed)
