// API PARA EL REGISTRY

const express = require("express");

const app = express();

// Se define el puerto
const port=3000;

app.get("/",(req, res) => {

res.json({message:'Página de inicio de aplicación de ejemplo de SD'})
});

const sqlite3 = require("sqlite3").verbose();
const bodyParser = require("body-parser");

// Configuración de la conexión a la base de datos SQLite
const dbPath = "./SD_API_WEB"; // Ruta al archivo de la base de datos SQLite
const db = new sqlite3.Database(dbPath, sqlite3.OPEN_READWRITE, (err) => {
  if (err) {
    console.error("Error al abrir la base de datos", err.message);
  } else {
    console.log(`Conexión a la base de datos ${dbPath} correcta`);
  }
});

// Middleware para procesar datos en formato JSON
app.use(bodyParser.json());

// Listado de todos los usuarios
app.get("/usuarios", (req, res) => {
  console.log('Listado de todos los usuarios');
  
  db.all("SELECT * FROM Usuarios", (err, rows) => {
    if (err) {
      console.error("Error al ejecutar la consulta", err.message);
      res.status(500).send("Error en el servidor");
    } else {
      res.json(rows);
    }
  });
});

// Datos de un solo usuario
app.get("/usuarios/:id", (req, res) => {
   console.log('Obtener datos de un usuario');
   
   const {id} = req.params;

   db.all("Select * FROM Usuarios WHERE idUsuario = " + id, (err,rows) => {
     if (err) {
     	console.error("Error al ejecutar la consulta", err.message);
     	res.status(500).send("Error en el servidor");
     } else {
     	res.json(rows);
     }
   });
});

// Manejar errores 404
app.use((req, res) => {
  res.status(404).send("Ruta no encontrada");
});

// Iniciar el servidor en el puerto 3000
app.listen(port, () => {
  console.log(`Servidor iniciado en http://localhost:${port}`);
});

