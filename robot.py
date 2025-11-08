from gpiozero import PWMOutputDevice, DigitalOutputDevice
from gpiozero.pins.lgpio import LGPIOFactory
import lgpio
import time

class Robot:
  def __init__(self):
    # Motor pin mapping
    self.motors = {
      'M1': {'IN1': 24, 'IN2': 23, 'EN': 18},
      'M2': {'IN1': 16, 'IN2': 26, 'EN': 12},
      'M3': {'IN1': 6,  'IN2': 5,  'EN': 13},
      'M4': {'IN1': 20, 'IN2': 21, 'EN': 19},
    }

    self.speed = 0.75
    self.pin_factory = LGPIOFactory()

    # Setup motor pins
    for _, m in self.motors.items():
      m['L_IN'] = DigitalOutputDevice(m['IN1'], pin_factory=self.pin_factory)
      m['R_IN'] = DigitalOutputDevice(m['IN2'], pin_factory=self.pin_factory)
      m['PWM']  = PWMOutputDevice(m['EN'], frequency=1000, pin_factory=self.pin_factory)

    # ======== Tambahan: Setup sensor Ping Parallax ========
    self.ping_pin = 4  # misalnya pakai GPIO4
    self.chip = self.pin_factory.chip
    lgpio.gpio_claim_output(self.chip, self.ping_pin)  # awalnya mode output

  # ========================================================
  # =============== SENSOR PING PARALLAX ===================
  # ========================================================
  def baca_jarak(self):
    """Mengukur jarak (cm) dari sensor Ping Parallax."""
    TRIGGER_PIN = self.ping_pin
    chip = self.chip

    # Kirim trigger pulse 10us
    lgpio.gpio_write(chip, TRIGGER_PIN, 1)
    time.sleep(10e-6)
    lgpio.gpio_write(chip, TRIGGER_PIN, 0)

    # Ganti pin jadi input untuk baca echo
    lgpio.gpio_claim_input(chip, TRIGGER_PIN)

    # Tunggu sampai sinyal naik
    start_time = time.time()
    while lgpio.gpio_read(chip, TRIGGER_PIN) == 0:
      start_time = time.time()

    # Tunggu sampai sinyal turun
    while lgpio.gpio_read(chip, TRIGGER_PIN) == 1:
      end_time = time.time()

    # Kembalikan ke mode output lagi
    lgpio.gpio_claim_output(chip, TRIGGER_PIN)

    # Hitung jarak (dalam cm)
    pulse_duration = end_time - start_time
    distance_cm = pulse_duration * 17150  # speed of sound (34300/2)

    return round(distance_cm, 2)

  # ========================================================
  # ================= MOTOR FUNCTIONS ======================
  # ========================================================
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
    for m in self.motors.values():
      self.motor_stop(m)

  def maju(self, speed=0):
    for m in self.motors.values():
      self.motor_forward(m, speed)

  def mundur(self, speed=0):
    for m in self.motors.values():
      self.motor_backward(m, speed)

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
