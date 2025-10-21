from robot import Robot
import socketio
import eventlet
import time
import json
import os

# ===============================
# CONFIGURASI DASAR
# ===============================
ENV_FILE = os.path.join(os.path.dirname(__file__), "env.json")
_env_ = {}
if os.path.exists(ENV_FILE):
  with open(ENV_FILE, "r") as f:
    _env_ = json.load(f)

HOST = _env_.get("HOST", "0.0.0.0")
PORT = _env_.get("PORT", 3210)
DEBUG = _env_.get("DEBUG", True)

# ===============================
# INISIALISASI SERVER
# ===============================
sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio)

# ===============================
# INISIALISASI ROBOT
# ===============================
robot = Robot()

# ===============================
# EVENT HANDLER
# ===============================
@sio.event
def connect(sid, environ):
  print(f"Client connected: {sid}")

@sio.event
def disconnect(sid):
  print(f"Client disconnected: {sid}")

@sio.on("perintah")
def on_perintah(sid, command):
  if DEBUG:
    print(f"[PERINTAH] {command}")
  handle_command(command)

@sio.on("run_commands")
def on_run_commands(sid, commands):
  if DEBUG:
    print(f"[RUN COMMANDS] {commands}")
  run_commands(commands)

@sio.on("ping_robot")
def on_ping(sid, data):
  sio.emit("pong_robot", {"status": "ok"})
  if DEBUG:
    print(f"[PING] dari {sid}")

# ===============================
# LOGIKA KONTROL ROBOT
# ===============================
def handle_command(command):
  if "move|" in command:
    parse_move_command(command)
  else:
    move_commands(command)

def move_commands(command, speed=0, _time=0.0):
  if command == "berhenti":
    robot.berhenti()
  elif command == "maju":
    robot.maju(speed)
  elif command == "mundur":
    robot.mundur(speed)
  elif command == "kiri":
    robot.kiri(speed)
  elif command == "kanan":
    robot.kanan(speed)
  elif command == "mundur_kiri":
    robot.mundur_kiri(speed)
  elif command == "mundur_kanan":
    robot.mundur_kanan(speed)
  elif command == "putar_kiri":
    robot.putar_kiri(speed)
  elif command == "putar_kanan":
    robot.putar_kanan(speed)
  
  wait_time_to_stop(_time)

def parse_move_command(command):
  try:
    _, data = command.split("|")
    cmd, time_and_speed = data.split(":")
    _time, speed = time_and_speed.split(",")
    move_commands(cmd, float(speed) / 100, float(_time))
  except Exception as e:
    print("[ERROR parse_move_command]", e)

def wait_time_to_stop(_time):
  if _time <= 0:
    return
  time.sleep(_time)
  robot.berhenti()

def run_commands(commands):
  for c in commands:
    cmd = f"move|{c['type']}:{c['time']},{c['speed']}"
    parse_move_command(cmd)

# ===============================
# MAIN LOOP
# ===============================
if __name__ == "__main__":
  print(f"🚀 Socket.IO robot server running on {HOST}:{PORT}")
  print("Waiting for clients...\n")
  try:
    eventlet.wsgi.server(eventlet.listen((HOST, PORT)), app)
  except KeyboardInterrupt:
    robot.berhenti()
    print("Robot stopped manually.")
