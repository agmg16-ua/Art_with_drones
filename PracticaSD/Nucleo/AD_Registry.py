import socket
import uuid
import sys
import threading
import sqlite3
import ssl

#Librerías para API_REST
from flask import Flask, request
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy

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
@app.route('/obtenerdatos', methods=['GET'])
def get_items():
    try:
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
        # Handle any exceptions that may occur during the process
        response = {
            'error': False,
            'message': f'Error Occurred: {e}',
            'data': None
        }
        # Return a JSON response with HTTP status code 500 (Internal ServerError)
        return jsonify(response), 500

#Añade una serie de elementos en la base de datos
@app.route('/unirme', methods=['POST'])
def add_items():
    global id_nueva
    existe = False

    try:
        if request.method == "POST":
            # Get the JSON data from the request
            datas = request.get_json()
            print(datas)
            # Conectar a la base de datos (creará el archivo si no existe)
            conn = sqlite3.connect('registry')
            # Crear un cursor para ejecutar comandos SQL
            cursor = conn.cursor()
            data = []
            # Consultar datos

            cursor.execute('SELECT * FROM drones')
            data = cursor.fetchall()

            for item in data:
                if item[0] == datas['id']:
                    existe = True

            token = ""
            if existe == False:
                # Create a cursor object for interacting with the MySQL database
                # Extract the 'alias' and 'token' fields from the JSON data
                id = datas['id']
                alias = datas['alias']
                agregarlo = "INSERT INTO drones (id, id_virtual, alias, token) VALUES (?, ?, ?, ?)"

                token = generar_token()
                cursor.execute(agregarlo, (int(id),int(id_nueva),alias, token))
                # Execute an SQL query to insert the 'alias' and 'token' into the 'drones' table
                #cur.execute('INSERT INTO drones (alias, token) VALUES (%s, %s)',(alias, token))
                # Commit the changes to the database
                conn.commit()
                # Create a response dictionary for a successful operation
                data = [{'id': id, 'id_virtual': id_nueva, 'alias': alias, 'token': token}]
                id_nueva += 1

                response = {
                    'error' : False,
                    'message': 'Item Added Successfully',
                    'data': data
                }
            else:
                agregartoken = "UPDATE drones SET token = ? WHERE id = ?"
                token = generar_token()
                cursor.execute(agregartoken,(token,datas['id']))

                # Execute an SQL query to insert the 'alias' and 'token' into the 'drones' table
                #cur.execute('INSERT INTO drones (alias, token) VALUES (%s, %s)',(alias, token))
                # Commit the changes to the database
                conn.commit()
                data = [{'id': datas['id'],'token': token}]

                response = {
                    'error' : False,
                    'message': 'Item Updated Successfully',
                    'data': data
                }

            # Close the database cursor
            conn.close()

            # Return a JSON response with HTTP status code 201 (Created)
        return jsonify(response), 201
    except Exception as e:
        # Handle any exceptions that may occur during the process
        response = {
            'error' : False,
            'message': f'Error Ocurred: {e}',
            'data': None
        }
        # Return a JSON response with HTTP status code 500 (Internal ServerError)
        return jsonify(response), 500

#Actualiza el item correspondiente a la id pasada como parametro, Aqui no deberiamos tener que actualizar valores
"""
@app.route('/updateitems/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    try:
        # Get the JSON data from the request
        datas = request.get_json()
        print(datas)
        # Extract the 'name' and 'id' fields from the JSON data
        id = datas['id']
        alias = datas['alias']

        # Create a cursor object for interacting with the MySQL database
        cur = mysql.connection.cursor()
        # Execute an SQL query to update the 'alias' and 'token' of an item with a specific 'item_id'
        cur.execute('UPDATE drones SET alias = %s, id = %s WHERE id = %s', (alias, item_id))
        # Commit the changes to the database
        mysql.connection.commit()
        # Close the database cursor
        cur.close()
        # Create a response dictionary for a successful update
        response = {
            'error' : False,
            'message': 'Item Updated Successfully',
            'data': { 'item_id': item_id }
        }
        # Return a JSON response with HTTP status code 201 (Created)
        return jsonify(response), 201
    except Exception as e:
        # Handle any exceptions that may occur during the process
        response = {
            'error' : False,
            'message': f'Error Occurred: {e}',
            'data': None
        }
        # Return a JSON response with HTTP status code 500 (Internal ServerError)
        return jsonify(response), 500
"""

#Elimina el item con la id pasada por parámetro. EL cliente no debería poder eliminar nada
"""
@app.route('/deleteitems/<int:item_id>', methods=['DELETE'])
def delete_items(item_id):
    try:
        # Create a cursor object for interacting with the MySQL database
        cur = mysql.connection.cursor()
        # Execute an SQL query to delete an item with a specific 'item_id'
        cur.execute('DELETE FROM drones WHERE id = %s', (item_id,))
        # Commit the changes to the database
        mysql.connection.commit()
        # Close the database cursor
        cur.close()
        # Create a response dictionary for a successful deletion
        response = {
            'error' : False,
            'message': 'Item Deleted Successfully',
            'data': { 'item_id': item_id }
        }
        # Return a JSON response with HTTP status code 201 (Created)
        return jsonify(response), 201
    except Exception as e:
        # Handle any exceptions that may occur during the process
        response = {
            'error' : False,
            'message': f'Error Occurred: {e}',
            'data': None
        }
        # Return a JSON response with HTTP status code 500 (Internal ServerError)
        return jsonify(response), 500
"""

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
def generar_token():
    token = str(uuid.uuid4())
    return token

#Vacia el fichero antiguo de drones antes de empezar a registrar
def borrar_bd():
    try:
        app = Flask(__name__)

        # Conectar a la base de datos (creará el archivo si no existe)
        conn = sqlite3.connect('registry')

        # Crear un cursor para ejecutar comandos SQL
        cursor = conn.cursor()

        cursor.execute("DELETE FROM drones")
        conn.commit()

        conn.close()
    except Exception as e:
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

if __name__ == "__main__":
    """
    #Ejecuta el hilo para mantenerme a la escucha de las posiciones de los drones.
    controlarRegistry = threading.Thread(target=handleSockets,args=(len(sys.argv),int(sys.argv[1]),socket))
    controlarRegistry.start()
    """
    #Casa: '192.168.1.84'
    #EPS: 172.27.173.122
    #Movil: 192.168.218.43
    app.debug = True
    app.run(host='192.168.1.84')#,ssl_context=('certificados/certificado_registry.crt', 'certificados/clave_privada_registry.pem'))
