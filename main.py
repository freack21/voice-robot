from robot import Robot
import socketio
import eventlet
import time
import json
import os
import threading

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
distance_debug_enabled = _env_.get("DISTANCE_DEBUG", False)

# ===============================
# INISIALISASI SERVER
# ===============================
sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio)

# ===============================
# INISIALISASI ROBOT
# ===============================
robot = Robot()

auto_stop = False

# ===============================
# THREAD UNTUK DEBUG JARAK
# ===============================
def distance_debug_loop():
  """Thread untuk menampilkan jarak setiap 1 detik"""
  while distance_debug_enabled:
    try:
      distance = robot.get_distance()
      if distance != -1:
        print(f"[DEBUG JARAK] {distance} cm")
      else:
        print("[DEBUG JARAK] Gagal membaca sensor")
    except Exception as e:
      print(f"[DEBUG JARAK ERROR] {e}")

    # Tunggu 1 detik
    time.sleep(1)

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

@sio.on("ping")
def on_ping(sid):
  global auto_stop
  if DEBUG:
    print(f"[PING] sending ping..")
  sio.emit("pong", {"auto_stop": auto_stop})

@sio.on("auto_stop")
def on_auto_stop(sid, state):
  global auto_stop
  if DEBUG:
    print(f"[AUTO STOP] set to '{state}'")
  auto_stop = state

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

@sio.on("toggle_distance_debug")
def on_toggle_distance_debug(sid, data):
  """Event untuk menyalakan/mematikan debug jarak dari client"""
  global distance_debug_enabled
  distance_debug_enabled = data.get("enabled", not distance_debug_enabled)
  status = "AKTIF" if distance_debug_enabled else "NONAKTIF"
  print(f"[DEBUG JARAK] {status}")
  sio.emit("distance_debug_status", {"enabled": distance_debug_enabled})

@sio.on("get_distance")
def on_get_distance(sid, data):
  """Event untuk mendapatkan jarak saat ini"""
  distance = robot.get_distance()
  sio.emit("current_distance", {"distance": distance})
  if DEBUG:
    print(f"[GET_DISTANCE] {distance} cm")

# ===============================
# LOGIKA KONTROL ROBOT
# ===============================
def handle_command(command):
  if "move|" in command:
    parse_move_command(command)
  else:
    move_commands(command)

def move_commands(command, speed=0, _time=0.0, max_distance=10):
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

  wait_time_to_stop(_time, max_distance)

def parse_move_command(command):
  try:
    _, data = command.split("|")
    cmd, _etc = data.split(":")
    _time, speed, max_distance = _etc.split(",")
    move_commands(cmd, float(speed) / 100, float(_time), float(max_distance))
  except Exception as e:
    print("[ERROR parse_move_command]", e)

def wait_time_to_stop(_time=0, obstacle_threshold=10):
  global auto_stop

  if _time <= 0:
    return

  start_time = time.time()

  while time.time() - start_time < _time:
    # kalau auto_stop aktif, cek jarak
    if auto_stop:
      try:
        distance = robot.get_distance()
        if distance != -1 and distance < obstacle_threshold:
          print(f"[AUTO STOP] Obstacle terdeteksi ({distance} cm), berhenti lebih awal!")
          robot.berhenti()
          return  # keluar dari fungsi lebih cepat
      except Exception as e:
        print(f"[AUTO STOP ERROR] {e}")

    time.sleep(0.1)  # cek setiap 100ms

  # kalau waktu habis dan gak ada obstacle
  robot.berhenti()

def run_commands(commands):
  for c in commands:
    cmd = f"move|{c['type']}:{c['duration']},{c['speed']},{c['max_distance']}"
    parse_move_command(cmd)

# ===============================
# FUNGSI CLEANUP
# ===============================
def cleanup():
  """Bersihkan resources sebelum exit"""
  global distance_debug_enabled
  distance_debug_enabled = False
  robot.berhenti()
  print("\n🛑 Robot berhenti dan resources dibersihkan")

# ===============================
# MAIN LOOP
# ===============================
if __name__ == "__main__":
  print(f"🚀 Socket.IO robot server running on {HOST}:{PORT}")
  print("Waiting for clients...\n")

  # Mulai thread debug jarak
  debug_thread = threading.Thread(target=distance_debug_loop, daemon=True)
  debug_thread.start()
  print("📊 Debug jarak aktif - menampilkan jarak setiap 1 detik")
  print("   Gunakan event 'toggle_distance_debug' untuk menonaktifkan\n")

  try:
    eventlet.wsgi.server(eventlet.listen((HOST, PORT)), app)
  except KeyboardInterrupt:
    cleanup()
    print("Robot stopped manually.")