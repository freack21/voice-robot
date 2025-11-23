// import basestation dependensi
const ENV = require("./env.json");
const express = require("express");
const chalk = require("chalk");
const { Server } = require("socket.io");
const http = require("http");
const { log } = require("console");

// membuat instans dari dependensi
const app = express();
const server = http.createServer(app);
const io = new Server(server);

// variabel essensial
let IP_basestation = "127.0.0.1";
const PORT_basestation = ENV.PORT || 3210;

// middlewares
app.use(express.json());

// routers
app.use((req, res, next) => {
  res.status(404).send("404 | Not found");
});
// routes

// variabel robot-robot
let onlineStatuses = {};
let id_robots = {};
let cmd_receivers = {};
let cmd_counters = {};

const initializeRobot = (username) => {
  onlineStatuses[username] = false;
  id_robots[username] = "";
  cmd_receivers[username] = true;
  cmd_counters[username] = 0;
};

const robotUsernames = ["aikargo"];
robotUsernames.forEach((d) => initializeRobot(d));

const sleep = async (ms) => {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
};

// socket.io events
io.on("connection", (socket) => {
  // event 'ping' untuk cek status online robot
  const ping = () => {
    io.emit("ping", {
      onlineStatuses,
      IP_basestation,
      PORT_basestation,
    });
    goodInfo("ping...");
  };

  const logging = (info, type = "basic") => {
    const logger = {
      good: chalk.greenBright,
      error: chalk.redBright,
      warning: chalk.yellowBright,
    };

    log((logger[type] || chalk)(info));
    io.emit("informasi", {
      info,
      type,
    });
  };

  const goodInfo = (info) => {
    logging(info, "good");
  };

  const warningInfo = (info) => {
    logging(info, "warning");
  };

  const errorInfo = (info) => {
    logging(info, "error");
  };

  // event 'join' saat robot tersambung ke basestation untuk identifikasi
  socket.on("join", (username) => {
    socket.username = username;

    if (!username) return;

    // event 'informasi' untuk kirim informasi terbaru
    goodInfo(`'${username}' terhubung ke Basestation!`);

    if (!robotUsernames.includes(username)) return;

    id_robots[username] = socket.id;
    onlineStatuses[username] = true;
    cmd_receivers[username] = true;
    cmd_counters[username] = 0;

    // event 'ping' kirim data robot terbaru
    ping();
  });

  // event 'disconnect' saat ada robot yang terputus koneksi
  socket.on("disconnect", () => {
    if (!socket.username) return;
    const username = socket.username;

    warningInfo(`'${username}' offline`);

    if (!robotUsernames.includes(username)) return;
    onlineStatuses[username] = false;

    // event 'ping' kirim data robot terbaru
    ping();
  });

  socket.on("ping", () => {
    ping();
  });

  const kirimPerintah = (perintah, robot) => {
    if (!onlineStatuses[robot]) {
      errorInfo(`${robot} : [OFFLINE] ${perintah}`);
      return;
    }

    id_robots[robot] && io.to(id_robots[robot]).emit("perintah", perintah);
    goodInfo(`${robot} : ${perintah}`);
  };

  //kirim perintah ke robot
  socket.on("kirim-perintah", ({ perintah, robot }) => {
    if (robotUsernames.includes(robot)) {
      kirimPerintah(perintah, robot);
    }
  });

  socket.on("run-commands", ({ commands, robot }) => {
    io.to(id_robots[robot]).emit("run_commands", commands || []);
    goodInfo(`${robot} : ${commands}`);
  });

  socket.on("set-autostop", ({ robot, autostop }) => {
    io.to(id_robots[robot]).emit("set_autostop", autostop);
    goodInfo(`${robot} : set_autostop ${autostop}`);
  });

  socket.on("get-autostop", ({ robot }) => {
    io.to(id_robots[robot]).emit("get_autostop");
    goodInfo(`${robot} : get_autostop`);
  });

  socket.on("post_autostop", ({ robot, autostop }) => {
    io.emit("post-autostop", { robot, autostop });
    goodInfo(`${robot} : post_autostop ${autostop}`);
  });
});

const os = require("os");
const networkInterfaces = os.networkInterfaces();

for (const [name, interfaces] of Object.entries(networkInterfaces)) {
  for (const details of interfaces) {
    if (details.family === "IPv4") {
      if (["wi-fi", "lan"].some((d) => name.toLowerCase().includes(d)))
        IP_basestation = details.address;
      log(
        chalk.green(
          `Basestation IP [${name}] : http://${details.address}:${PORT_basestation}`
        )
      );
    }
  }
}

// mulai server
server.listen(PORT_basestation, () =>
  log(`Basestation is running on http://localhost:${PORT_basestation} !!`)
);
