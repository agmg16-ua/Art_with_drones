import socket
import uuid
import sys
import threading

#Librerías para API_REST
from flask import Flask, request
from flask import jsonify
from flask_mysqldb import MySQL

#Se crea una
app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'

app.config['MYSQL_USER'] = 'victor'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'registry'

mysql = MySQL(app)

#Variables globales.
id_nueva = 1                #Id nueva para el drone que se quiera registrar
token_dron_actual = ""      #Token de acceso

@app.route('/obtenerdatos', methods=['GET'])
def get_items():
    try:
        if request.method == "GET":
            # Create a cursor object for interacting with the MySQL database
            cur = mysql.connection.cursor()
            # Execute an SQL query to select all items from the 'items' table
            cur.execute('SELECT * FROM drones')
            # Fetch all the data (items) from the executed query
            data = cur.fetchall()

            # es una tupla de tuplas, cada fila es una tupla
            # print (data[0][1])
            # Close the database cursor
            cur.close()

            # Create a list of dictionaries to structure the retrieved items
            items = [{'id': item[0], 'alias': item[1], 'token': item[2]} for item in data]
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

@app.route('/additems', methods=['POST'])
def add_items():
    try:
        # Get the JSON data from the request
        datas = request.get_json()
        print (datas)
        cur= mysql.connection.cursor()
        # Create a cursor object for interacting with the MySQL database
        for data in datas :
            # Extract the 'alias' and 'token' fields from the JSON data
            alias = data['alias']
            token = data['token']
            cur.execute('INSERT INTO drones (alias, token) VALUES (%s, %s)', (alias, token))
        # Execute an SQL query to insert the 'alias' and 'token' into the 'drones' table
        #cur.execute('INSERT INTO drones (alias, token) VALUES (%s, %s)',(alias, token))
        # Commit the changes to the database
        mysql.connection.commit()
        # Close the database cursor
        cur.close()
        # Create a response dictionary for a successful operation
        response = {
            'error' : False,
            'message': 'Item Added Successfully',
            'data': data
        }
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

@app.route('/updateitems/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    try:
        # Get the JSON data from the request
        datas = request.get_json()
        print(datas)
        # Extract the 'name' and 'description' fields from the JSON data
        alias = datas['alias']
        token = datas['token']
        # Create a cursor object for interacting with the MySQL database
        cur = mysql.connection.cursor()
        # Execute an SQL query to update the 'alias' and 'token' of an item with a specific 'item_id'
        cur.execute('UPDATE drones SET alias = %s, token = %s WHERE id = %s', (alias, token, item_id))
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

#Compruebo si el drone ya se ha registrado anteriormente
def existe_en_bd(id, alias):
    existe = False
    try:
        with open("drones.txt", "r") as archivo:
            for linea in archivo:
                palabras = linea.split()
                if palabras[1] == id:
                    existe = True
                    token_dron_actual = palabras[0]
    except Exception as e:
        print("Error al comprobar drones:", e)
    return existe

#Escribe en el fichero el token,la id real del drone, la id virtual del drone y el alias.
def escribir_bd(id, alias):
    global id_nueva
    global token_dron_actual
    with open("drones.txt", "a") as archivo:
        if not existe_en_bd(id, alias):
            token_dron_actual = generar_token()
            archivo.write(f"{token_dron_actual} {id} {id_nueva} {alias}\n")
            id_nueva += 1

#Genera un token de acceso
def generar_token():
    token = str(uuid.uuid4())
    return token

#Vacia el fichero antiguo de drones antes de empezar a registrar
def borrar_fichero():
    try:
        with open("drones.txt", "w") as archivo:
            archivo.truncate(0)
        print("El fichero ha sido vaciado con éxito.")
    except Exception as e:
        print("Error al vaciar el fichero:", e)

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
        borrar_fichero()
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

if __name__ == "__main__":
    #Ejecuta el hilo para mantenerme a la escucha de las posiciones de los drones.
    controlarRegistry = threading.Thread(target=handleSockets,args=(len(sys.argv),int(sys.argv[1]),socket))
    controlarRegistry.start()

    app.debug = True
    app.run(host='172.27.173.122',ssl_context=('certificados/cert.pem', 'certificados/key.pem'))
