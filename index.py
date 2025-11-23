from robot import Robot
import socketio
import json
import os
import time

ENV_FILE = os.path.join(os.path.dirname(__file__), "env.json")
_env_ = {}
with open(ENV_FILE, "r") as f:
  _env_ = json.load(f)

sio = socketio.Client()
def initSocketIO(alamatIP) :
  global sio
  sio.connect(alamatIP)

class SocketConn :
  global sio

  def __init__(self) :
    self.initRobot()
    self.initGlobalVars()
    initSocketIO(self.alamatIP)


  # ++++++++++++++++++++++++++++++++++++
  def initRobot(self) :
    self.robot = Robot()

  def initGlobalVars(self) :
    self.myUsername = "aikargo"
    self.alamatIP = _env_.get("WS_URL", "http://192.168.137.1:3210/")
    self.is_debug = _env_.get("DEBUG", True)
    self.distance_debug_enabled = _env_.get("DISTANCE_DEBUG", False)

    self.autostop = False
    self.distance = 0


  # ++++++++++++++++++++++++++++++++++++
  @sio.on("connect")
  def on_connect(self):
    print(f"'{self.myUsername}' connected to Socket.IO server!")
    sio.emit('join', self.myUsername)

  @sio.on("disconnect")
  def on_disconnect(self):
    print(f"'{self.myUsername}' disconnected from Socket.IO server!")

  @sio.on("perintah")
  def on_perintah(self, command):
    if self.is_debug:
      print(f'perintah: {command}')
    self.handle_command(command)

  @sio.on("run_commands")
  def on_run_commands(self, commands):
    if self.is_debug:
      print(f'commands: {commands}')
    self.run_commands(commands)

  @sio.on("set_autostop")
  def on_set_autostop(self, autostop):
    if self.is_debug:
      print(f'set autostop to {autostop}')
    self.autostop = autostop
    sio.emit("post_autostop", { "autostop": self.autostop, "robot": self.myUsername })

  @sio.on("get_autostop")
  def on_get_autostop(self):
    if self.is_debug:
      print(f'autostop: {self.autostop}')
    sio.emit("post_autostop", { "autostop": self.autostop, "robot": self.myUsername })

  @sio.on("get_distance")
  def on_get_distance(self):
    if self.is_debug:
      print(f'distance: {self.distance}')
    sio.emit("post_distance", { "distance": self.distance, "robot": self.myUsername })


  # ++++++++++++++++++++++++++++++++++++
  def handle_command(self, command):
    if "move|" in command:
      self.parse_move_command(command)
    else :
      self.move_commands(command)

  def move_commands(self, command, speed=0, _time=0.0, max_distance=30):
    if command == "berhenti":
      self.robot.berhenti()
    elif command == "maju":
      self.robot.maju(speed)
    elif command == "mundur":
      self.robot.mundur(speed)
    elif command == "kiri":
      self.robot.kiri(speed)
    elif command == "kanan":
      self.robot.kanan(speed)
    elif command == "mundur_kiri":
      self.robot.mundur_kiri(speed)
    elif command == "mundur_kanan":
      self.robot.mundur_kanan(speed)
    elif command == "putar_kiri":
      self.robot.putar_kiri(speed)
    elif command == "putar_kanan":
      self.robot.putar_kanan(speed)

    self.wait_time_to_stop(_time, max_distance)

  def parse_move_command(self, command):
    [_, data] = command.split("|")
    [cmd, _etc] = data.split(":")
    [_time, speed, max_distance] = _etc.split(",")
    self.move_commands(cmd, float(speed) / 100, float(_time), float(max_distance))


  def wait_time_to_stop(self, _time=0, obstacle_threshold=30):
    if _time <= 0:
      return

    start_time = time.time()

    while time.time() - start_time < _time:
      # kalau auto_stop aktif, cek jarak
      if self.autostop:
        try:
          distance = self.robot.get_distance()
          if distance != -1 and distance < obstacle_threshold:
            print(f"[AUTO STOP] Obstacle terdeteksi ({distance} cm), berhenti lebih awal!")
            self.robot.berhenti()
            return  # keluar dari fungsi lebih cepat
        except Exception as e:
          print(f"[AUTO STOP ERROR] {e}")

      # time.sleep(0.1)  # cek setiap 100ms

    # kalau waktu habis dan gak ada obstacle
    self.robot.berhenti()

  def run_commands(self, commands):
    for command in commands:
      cmd = f"move|{command['type']}:{command['time']},{command['speed']},{c['max_distance']}"
      self.parse_move_command(cmd)



  # ++++++++++++++++++++++++++++++++++++
  def run(self) :
    start_time = time.time()
    try:
      while True:
        if self.distance_debug_enabled and time.time() - start_time > 1:
          try:
            distance = self.robot.get_distance()
            if distance != -1:
              print(f"[DEBUG JARAK] {distance} cm")
              self.distance = distance
            else:
              print("[DEBUG JARAK] Gagal membaca sensor")
              self.distance = -1
          except Exception as e:
            print(f"[DEBUG JARAK ERROR] {e}")
            self.distance = -1

          start_time = time.time()
    except KeyboardInterrupt:
      self.robot.berhenti()
      print("Mematikan Robot..")

if __name__ == '__main__':
  node = SocketConn()
  node.run()