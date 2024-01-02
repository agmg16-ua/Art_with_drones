// API PARA EL REGISTRY

const express = require("express");

const app = express();

const cors = require("cors");

// Se define el puerto
const port = 3000;

app.use(cors());

const winston = require('winston');

const requestIp = require('request-ip');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp({
      format: 'YYYY-MM-DD HH:mm:ss'
    }),
    winston.format.printf(info => {
      return `${info.timestamp} - ${info.level.toUpperCase()} - Acción: ${info.label} - IP: ${info.ip} - Descripción: ${info.message}`;
    })
  ),
  defaultMeta: { service: 'user-service' },
  transports: [
    new winston.transports.File({ filename: '../auditoria.log' })
  ]
});

app.use(requestIp.mw())

app.get("/", (req, res) => {
  const ip = req.clientIp;
  logger.log({
    level: 'info',
    message: 'Página de inicio de aplicación de ejemplo de SD',
    label: 'app.get("/")',
    ip: ip
  });

  res.json({ message: "Página de inicio de aplicación de ejemplo de SD" });
});

const sqlite3 = require("sqlite3").verbose();
const bodyParser = require("body-parser");

const os = require('os');

// Obtener las interfaces de red
const networkInterfaces = os.networkInterfaces();

// Obtener la dirección IP de la primera interfaz de red (excluyendo la interfaz de loopback)
let ip;
for (let name of Object.keys(networkInterfaces)) {
  for (let interface of networkInterfaces[name]) {
    if ('IPv4' !== interface.family || interface.internal !== false) {
      continue;
    }
    ip = interface.address;
  }
}

// Configuración de la conexión a la base de datos SQLite
const dbPath = "./../registry"; // Ruta al archivo de la base de datos SQLite
const db = new sqlite3.Database(dbPath, sqlite3.OPEN_READWRITE, (err) => {
  if (err) {
    logger.log({
      level: 'error',
      message: 'Error al abrir la base de datos' + err.message,
      label: 'db',
      ip: ip
    });
    console.error("Error al abrir la base de datos", err.message);
  } else {
    logger.log({
      level: 'info',
      message: 'Conexión a la base de datos correcta',
      label: 'db',
      ip: ip
    });
    console.log(`Conexión a la base de datos ${dbPath} correcta`);
  }
});

// Middleware para procesar datos en formato JSON
app.use(bodyParser.json());

// Listado de todos los drones
app.get("/drones", (req, res) => {
  const ip = req.clientIp;
  logger.log({
    level: 'info',
    message: 'Listando los drones registrados',
    label: 'app.get("/drones")',
    ip: ip
  });

  console.log("Listando los drones registrados...");

  db.all("SELECT * FROM Drones", (err, rows) => {
    if (err) {
      logger.log({
        level: 'error',
        message: 'Error al ejecutar la consulta' + err.message,
        label: 'db',
        ip: ip
      });
      console.error("Error al ejecutar la consulta", err.message);
      res.status(500).send("Error en el servidor");
    } else {
      logger.log({
        level: 'info',
        message: 'Listado de drones correcto',
        label: 'db',
        ip: ip
      });
      res.json(rows);
    }
  });
});

// Visualización del mapa
app.get("/mapa", (req, res) => {
  const ip = req.clientIp;
  logger.log({
    level: 'info',
    message: 'Mostrando mapa',
    label: 'app.get("/mapa")',
    ip: ip
  });
  console.log("Mostrando mapa...");

  db.all("Select * FROM Mapa", (err, rows) => {
    if (err) {
      logger.log({
        level: 'error',
        message: 'Error al ejecutar la consulta' + err.message,
        label: 'db',
        ip: ip
      });
      console.error("Error al ejecutar la consulta", err.message);
      res.status(500).send("Error en el servidor");
    } else {
      logger.log({
        level: 'info',
        message: 'Mapa mostrado correctamente',
        label: 'db',
        ip: ip
      });
      res.json(rows);
    }
  });
});

// Visualización de los estados de los componentes
app.get("/estados", (req, res) => {
  const ip = req.clientIp;
  logger.log({
    level: 'info',
    message: 'Mostrando estados de componentes',
    label: 'app.get("/estados")',
    ip: ip
  });
  console.log("mostrando estados de componentes...");

  db.all("Select * FROM Estados", (err, rows) => {
    if (err) {
      logger.log({
        level: 'error',
        message: 'Error al ejecutar la consulta' + err.message,
        label: 'db',
        ip: ip
      });
      console.error("Error al ejecutar la consulta", err.message);
      res.status(500).send("Error en el servidor");
    } else {
      logger.log({
        level: 'info',
        message: 'Estados de componentes mostrados correctamente',
        label: 'db',
        ip: ip
      });
      res.json(rows);
    }
  });
});

// Manejar errores 404
app.use((req, res) => {
  const ip = req.clientIp;
  logger.log({
    level: 'error',
    message: 'Ruta no encontrada',
    label: 'app.use((req, res)',
    ip: ip
  });
  res.status(404).send("Ruta no encontrada");
});

// Iniciar el servidor en el puerto 3000
app.listen(port, () => {
  logger.log({
    level: 'info',
    message: 'Servidor iniciado en http://localhost:' + port,
    label: 'app.listen(port, ()',
    ip: ip
  });
  console.log(`Servidor iniciado en http://localhost:${port}`);
});
