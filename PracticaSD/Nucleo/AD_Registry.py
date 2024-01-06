import socket
import uuid
import sys
import time
import threading
import sqlite3
import ssl

#Librerías para API_REST
from flask import Flask, request,abort
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy

#Libreria para auditoria
import logging

#Librerias seguridad
import hashlib
from functools import wraps

# Obtiene la dirección IP local de la red actual
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ip_address = s.getsockname()[0]
s.close()

# Configurar el sistema de registro
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.FileHandler('auditoria.log')
handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - Acción: %(funcName)s - IP: ' + ip_address + ' - Descripción: %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)

# Decorador para asignar un Logger con IP a la función
def logger_decorator(func):
    def wrapper(*args, **kwargs):
        func.logger = logger
        return func(*args, **kwargs)
    return wrapper

#Decorador api_key
def require_api_key(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        with open('API_KEY_REGISTRY.txt', 'r') as file:
            api_key = file.read().strip()
        if request.headers.get('x-api-key') != api_key:
            abort(401)
        return view_function(*args, **kwargs)
    return decorated_function

#Se crea una
app = Flask(__name__)

#context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
#context.load_cert_chain(certfile='certificados/certificado_registry.crt', keyfile='certificados/clave_privada_registry.pem')

#db = SQLAlchemy(app)

# Definir el modelo de la tabla de usuarios
#class Drones(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    id_virtual = db.Column(db.Integer, nullable=False)
#    alias = db.Column(db.String(50), nullable=False)
#    token = db.Column(db.String(255), nullable=False)

#Variables globales.
id_nueva = 1                #Id nueva para el drone que se quiera registrar
token_dron_actual = ""      #Token de acceso

#Parte API_REST
#Obtendrá los datos que haya en la base de datos
@logger_decorator
@app.route('/obtenerdatos', methods=['GET'])
@require_api_key
def get_items():
    try:
        logger.info('Se ha solicitado obtener los datos de los drones de la base de datos')
        if request.method == "GET":
            # Conectar a la base de datos (creará el archivo si no existe)
            conn = sqlite3.connect('registry')

            # Crear un cursor para ejecutar comandos SQL
            cursor = conn.cursor()

            # Consultar datos
            cursor.execute('SELECT * FROM drones')
            data = cursor.fetchall()

            # Create a list of dictionaries to structure the retrieved items
            items = [{'id': item[0], 'id_virtual': item[1], 'alias': item[2], 'token': item[3]} for item in data]

            # Create a response dictionary for a successful operation
            response = {
                'data':items,
                'error': False,
                'message': 'Items Fetched Successfully'
            }
            # Return a JSON response with HTTP status code 200 (OK)
            return jsonify(response), 200
    except Exception as e:
        logger.error(f'Error al obtener los datos de los drones de la base de datos: {e}')
        # Handle any exceptions that may occur during the process
        response = {
            'error': False,
            'message': f'Error Occurred: {e}',
            'data': None
        }
        # Return a JSON response with HTTP status code 500 (Internal ServerError)
        return jsonify(response), 500

#Añade una serie de elementos en la base de datos
@logger_decorator
@app.route('/unirme', methods=['POST'])
@require_api_key
def add_items():
    global id_nueva
    existe = False
    existeDesactivados = False
    try:
        logger.info('Se ha solicitado añadir un nuevo drone a la base de datos')
        if request.method == "POST":
            # Get the JSON data from the request
            datas = request.get_json()
            print(datas)
            # Conectar a la base de datos (creará el archivo si no existe)
            conn = sqlite3.connect('registry')
            # Crear un cursor para ejecutar comandos SQL
            cursor = conn.cursor()
            # Consultar datos
            dataRes = []
            cursor.execute('SELECT * FROM drones')
            data = cursor.fetchall()
            
            for item in data:
                if item[0] == datas['id']:
                    existe = True
                    break

            token = ""
            
            if existe == False:
                # Create a cursor object for interacting with the MySQL database
                # Extract the 'alias' and 'token' fields from the JSON data
                id = datas['id']
                alias = datas['alias']
                agregarlo = "INSERT INTO drones (id, id_virtual, alias, token, posicion, fin, activos) VALUES (?, ?, ?, ?, ?, ?, ?)"

                token = generar_token()
                token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
                
                cursor.execute(agregarlo, (int(id),int(id_nueva),alias, token_hash, "[0, 0]", "no", 1))
                # Execute an SQL query to insert the 'alias' and 'token' into the 'drones' table
                #cur.execute('INSERT INTO drones (alias, token) VALUES (%s, %s)',(alias, token))
                # Commit the changes to the database
                conn.commit()
                
                # Create a response dictionary for a successful operation
                dataRes = [{'id': id, 'id_virtual': id_nueva, 'alias': alias, 'token': token}]
                id_nueva += 1

                response = {
                    'error' : False,
                    'message': 'Item Added Successfully',
                    'data': dataRes
                }
                
                cursor.execute(agregarlo, (int(id),int(id_nueva),alias, token_hash, "[0, 0]", "no"))
                
                # Execute an SQL query to insert the 'alias' and 'token' into the 'drones' table
                #cur.execute('INSERT INTO drones (alias, token) VALUES (%s, %s)',(alias, token))
                # Commit the changes to the database
                conn.commit()
                
                id_nueva += 1
            else:
                agregartoken = "UPDATE drones SET token = ? WHERE id = ?"
                actualizarActivo = "UPDATE drones SET activos = ? WHERE id = ?"
                
                token = generar_token()
                
                token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
                cursor.execute(agregartoken,(token_hash,datas['id']))
                cursor.execute(actualizarActivo,(1,datas['id']))
                
                # Commit the changes to the database
                conn.commit()
                
                dataRes = [{'id': datas['id'],'token': token}]

                response = {
                    'error' : False,
                    'message': 'Item Updated Successfully',
                    'data': dataRes
                }

            #Ejecuta el hilo para controlar el token.
            expirar_token = threading.Thread(target=controlar_token,args=(id,))
            expirar_token.start()

            # Close the database cursor
            conn.close()

            # Return a JSON response with HTTP status code 201 (Created)
        return jsonify(response), 201
    except Exception as e:
        logger.error(f'Error al añadir un nuevo drone a la base de datos: {e}')
        # Handle any exceptions that may occur during the process
        response = {
            'error' : False,
            'message': f'Error Ocurred: {e}',
            'data': None
        }
        # Return a JSON response with HTTP status code 500 (Internal ServerError)
        return jsonify(response), 500

"""
#Parte mediante sockets
#Lee el sokcet con el drone de forma controlada
def leer_socket(sock, datos):
    try:
        datos = sock.recv(1024).decode('utf-8')
    except Exception as e:
        print("Error leyendo el socket: ", e)
    return datos

#Escribe en el socket de forma controlada
def enviar_socket(sock, token):
    try:
        sock.send(token.encode('utf-8'))
    except Exception as e:
        print("Error escribiendo en el socket: ", e)

#Escribe en el fichero el token,la id real del drone, la id virtual del drone y el alias.
def escribir_bd(id, alias):
    global id_nueva
    global token_dron_actual
    existe = False
    try:
        app = Flask(__name__)
        app.config['MYSQL_HOST'] = 'localhost'

        app.config['MYSQL_USER'] = 'victor'
        app.config['MYSQL_PASSWORD'] = 'password'
        app.config['MYSQL_DB'] = 'registry'

        mysql = MySQL(app)

        with app.app_context():
            cur = mysql.connection.cursor()

            id_virtual = id_nueva
            id_nueva += 1
            token_dron_actual = "Puede entrar"

            cur.execute('SELECT * FROM drones')
            # Fetch all the data (items) from the executed query
            data = cur.fetchall()

            for item in data:
                if item[0] == id:
                    token_dron_actual = item[3]
                    existe = True
                    break

            if existe == False:
                cur.execute('INSERT INTO drones (id, id_virtual , alias, token) VALUES (%s, %s, %s, %s)', (id, id_virtual, alias, token_dron_actual))
                # Confirmar los cambios en la base de datos
                mysql.connection.commit()

            # Close the database cursor
            cur.close()
    except Exception as e:
        print("Error escribiendo bd:", e)
"""
#Genera un token de acceso
@logger_decorator
def generar_token():
    logger.info('Se ha generado un nuevo token de acceso')
    token = str(uuid.uuid4())
    return token

#Vacia el fichero antiguo de drones antes de empezar a registrar
@logger_decorator
def borrar_bd():
    try:
        logger.info('Se ha solicitado vaciar el fichero de drones')
        app = Flask(__name__)

        # Conectar a la base de datos (creará el archivo si no existe)
        conn = sqlite3.connect('registry')

        # Crear un cursor para ejecutar comandos SQL
        cursor = conn.cursor()

        cursor.execute("DELETE FROM drones")
        conn.commit()

        conn.close()
    except Exception as e:
        logger.error(f'Error al vaciar el fichero de drones: {e}')
        print("Error al vaciar el fichero:", e)

"""
#Controla los drones que se quieran conectar por sockets
def handleSockets(num_args,puerto_args,socket):
    try:
        #Comprueba los argumentos
        if num_args < 2:
            print("Faltan argumentos: <Puerto de escucha>")
            sys.exit(-1)

        #Los asigna
        puerto = puerto_args

        #Vacia el fichero y crea el servidor a la espera de nuevos drones
        borrar_bd()

        Ssocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        Ssocket.bind(('', puerto))
        Ssocket.listen()

        #Realiza el registro del drone
        while True:
            print("Esperando solicitud...")
            socket, _ = Ssocket.accept()
            print("Recibida solicitud...")

            peticion = leer_socket(socket, "")
            print(peticion)
            palabras = peticion.split()

            escribir_bd(palabras[0], palabras[1])

            enviar_socket(socket, token_dron_actual)

        Ssocket.close()

    except Exception as e:
        print("Error:", e)
"""

@logger_decorator
def controlar_token(id):
    logger.info('Se ha iniciado el hilo para controlar el token de acceso')
    time.sleep(20)
    print("Ya es la horaaa")
    # Conectar a la base de datos (o crearla si no existe)
    conexion = sqlite3.connect('registry')

    # Crear un objeto cursor
    cursor = conexion.cursor()

    # Sentencia SQL DELETE
    consulta_borrado = "UPDATE drones SET token = NULL WHERE id = ?"

    # Ejecutar la sentencia con el parámetro proporcionado
    cursor.execute(consulta_borrado, (id,))

    # Confirmar la transacción
    conexion.commit()

    # Cerrar la conexión
    conexion.close()
    logger.info('Se ha borrado el token de acceso del drone')

if __name__ == "__main__":
    """
    #Ejecuta el hilo para mantenerme a la escucha de las posiciones de los drones.
    controlarRegistry = threading.Thread(target=handleSockets,args=(len(sys.argv),int(sys.argv[1]),socket))
    controlarRegistry.start()
    """
    #Casa: '192.168.1.84'
    #EPS: 172.27.173.122
    #Movil: 192.168.218.43
    #Alex: 192.168.0.35
    borrar_bd()
    app.debug = True
    app.run(host='192.168.1.84')
