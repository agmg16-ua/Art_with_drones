import socket
import random
import threading
import time
import requests
import json
from confluent_kafka import Consumer, Producer, KafkaError

#Crea el consumidor de destinos, de mapa y el productor de posiciones
#Clase principal.
class AD_Drone:
    #Inicializa la accion con el broker de kafka y la id del drone.
    #Además almacenará la posicion final del drone y la posicion actual del mismo como [x,y]
    #Tendrá el estado del drone y el mapa recibido por kafka, además de un booleano para detener la accion.
    def __init__(self, alias):
        self.alias = alias
        self.id = random.randint(1, 10000)
        self.id_virtual = -1
        self.token = ""
        self.broker = ""
        self.posicionFin = [None, None]
        self.posicionActual = [0, 0]
        self.estado = "Rojo"  # En movimiento "Rojo" y en la posición final "Verde"
        ###self.mapa = ""
        self.detener = False
        self.auto = False #Si es true se ejecuta automaticamente

    #Detiene la accion
    def detenerAccion(self):
        self.detener = True

    #Me uno a los topics con los roles correspondientes a Drone
    def consumidorDestino(self):
        # Configura las propiedades del consumidor
        config = {
            'bootstrap.servers': self.broker,  # Cambia esto a la dirección de tu cluster Kafka
            'group.id': 'grupo_' + str(self.id_virtual),
            'auto.offset.reset': 'latest',  # Comienza desde el inicio del topic
            'enable.auto.commit': False  # Deshabilita la confirmación automática
        }

        # Crea una instancia del consumidor
        consumidor = Consumer(config)

        return consumidor

    """
    def consumidorMapa(self):
        # Configura las propiedades del consumidor
        config = {
            'bootstrap.servers': self.broker,  # Cambia esto a la dirección de tu cluster Kafka
            'group.id': 'grupo_' + str(self.id_virtual),
            'auto.offset.reset': 'latest',  # Comienza desde el inicio del topic
            'enable.auto.commit': False  # Deshabilita la confirmación automática
        }

        # Crea una instancia del consumidor
        consumidor = Consumer(config)

        return consumidor
    """

    def productorPosiciones(self):
        # Configura las propiedades del productor
        config = {
            'bootstrap.servers': self.broker,  # Cambia esto a la dirección de tu cluster Kafka
        }

        # Crea una instancia del productor
        productor = Producer(config)

        return productor

    def productorActividad(self):
        # Configura las propiedades del productor
        config = {
            'bootstrap.servers': self.broker,  # Cambia esto a la dirección de tu cluster Kafka
        }

        # Crea una instancia del productor
        productor = Producer(config)

        return productor

    #Operaciones en kafka
    #Escuha todos los destinos de los drones y filtro para elegir el mío.
    #Al encontrarlo almaceno el destino en mi posicionFin.
    def escucharPorKafkaDestino(self, consumidor):
        try:
            topic = "destino"
            consumidor.subscribe(topics=[topic])

            while True:
                mensaje = consumidor.poll(0.1)
                if mensaje is not None:
                    if mensaje.error():
                        if mensaje.error().code() == KafkaError._PARTITION_EOF:
                            print('No más mensajes en la partición')
                            break
                        else:
                            print('Error al recibir mensaje: {}'.format(mensaje.error()))
                            break
                    else:
                        valores = mensaje.value().decode('utf-8').split()

                        if int(valores[0]) == self.id_virtual:
                            self.posicionFin[0] = int(valores[1])
                            self.posicionFin[1] = int(valores[2])
                            break
        except Exception as e:
            print("Error escuchando destino de drones: ",e)

    #Eschucho el estado del mapa mientras no se detenga la operación.
    #Almaceno el mapa en mi variable mapa como un string
    """
    def escucharEstadoMapa(self, consumidor):
        topic = "mapa"
        consumidor.subscribe(topics=[topic])

        while self.detener == False:
            mensaje = consumidor.poll(0.1)

            if mensaje is not None:
                if mensaje.error():
                    if mensaje.error().code() == KafkaError._PARTITION_EOF:
                        print('No más mensajes en la partición')
                    else:
                        print('Error al recibir mensaje: {}'.format(mensaje.error()))
                else:
                    self.mapa = str(mensaje.value().decode('utf-8'))
    """

    #Envio mi posicionActual al engine
    def enviarPosicion(self, productor):
        topic = "posiciones"

        productor.produce(topic, value=f"{self.id_virtual} {self.posicionActual[0]} {self.posicionActual[1]}")
        productor.flush()

    #Envio mi id y espero tres segundo
    def estoyActivo(self,productor):
        while self.detener == False:
            topic = "activos"

            productor.produce(topic, value=f"{self.id_virtual}")
            productor.flush()

    #Operaciones con el mapa
    #Cada vez que me muevo una casilla envio mi posicionActual al engine y espero 2 segundos.
    #Cuando haya llegado a mi destino me mantengo a la escucha de nuevos destinos.
    #Si escucho uno nuevo cambio el estado a rojo.
    def mover(self,productor,consumidorDestino):
        while self.detener == False:
            while self.estado != "Verde" and self.detener == False:
                if self.posicionFin[0] > self.posicionActual[0]:
                    self.posicionActual[0] += 1
                elif self.posicionFin[0] < self.posicionActual[0]:
                    self.posicionActual[0] -= 1

                if self.posicionFin[1] > self.posicionActual[1]:
                    self.posicionActual[1] += 1
                elif self.posicionFin[1] < self.posicionActual[1]:
                    self.posicionActual[1] -= 1

                if self.posicionFin[0] == self.posicionActual[0] and self.posicionFin[1] == self.posicionActual[1]:
                    self.estado = "Verde"
                time.sleep(1)
                self.enviarPosicion(productor)
            self.escucharPorKafkaDestino(consumidorDestino)

            self.estado = "Rojo"
            #if self.posicionActual[0] == 0 and self.posicionActual[1] == 0:
            #    self.detener = True

    #Este es el método principal de la clase. Crea los consumidores de destinos y el mapa,
    #y el productor de las posiciones del drone. Crea un hilo para moverse y otro para
    #escuchar el mapa constantemente. Luego despliega un menu donde da la opción de Imprimir
    #el mapa o salir el espectaculo,, deteniendo todos los hilos y volviendo al menu principal.
    def run(self):
        try:
            consumidorDestino = self.consumidorDestino()
            #####consumidorMapa = self.consumidorMapa()
            productorPosicion = self.productorPosiciones()
            productorActividad = self.productorActividad()

            #Los drones envian su id si se encuentran activos
            estoyActivo = threading.Thread(target=self.estoyActivo,args=(productorActividad,))
            estoyActivo.start()

            #Los drones envian su id si se encuentran activos
            estoyActivo = threading.Thread(target=self.escucharPorKafkaDestino,args=(consumidorDestino,))
            estoyActivo.start()
            
            destino = self.escucharPorKafkaDestino(consumidorDestino)

            #Los drones envian constantemente sus posiciones
            dronMovimiendose = threading.Thread(target=self.mover,args=(productorPosicion,consumidorDestino))
            dronMovimiendose.start()

            #Los drones escuchan constantemente el mapa
            ####dronEscuchaMapa = threading.Thread(target=self.escucharEstadoMapa,args=(consumidorMapa,))
            ######dronEscuchaMapa.start()

            #Menu con opcion de imprimir el mapa o detener la accion
            opcionAux = -1
            while opcionAux != 2 and self.detener == False:
                print("[1] Imprimir Mapa")
                print("[2] Salir del espectaculo")

                opcionAux = int(input())
                if opcionAux == 1:
                    print(self.mapa)
                elif opcionAux == 2:
                    self.detenerAccion()

        except Exception as e:
            print("Error durante la accion:", e)

    #Se registra con el registry mediante sockets y recibe el token de acceso.
    #Se mantiene leyendo del socket mientras no haya leido nada.
    #En el caso de que se caiga el registry saltará una excepción y se imprimirá por pantalla.
    """
    def registrarse(self, ip, puerto):
        try:
            cadena = f"{self.id} {self.alias}"
            skcliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            skcliente.connect((ip, int(puerto)))


            skcliente.send(cadena.encode('utf-8'))
            token = skcliente.recv(1024).decode('utf-8')

            self.token = token

            print("---Drone registrado de manera satisfactoria---\n")
            skcliente.close()

        except Exception as e:
            print("Error conectandose a registry: ",e)
    """

    def registrarse(self, ip, puerto):
        try:
            datos = {
                'id': self.id,
                'alias':self.alias
            }
            url= 'http://192.168.0.35:5000/unirme'
            response = requests.post(url,json=datos)#,verify='certificados/certificado_registry.crt')

            #if response.status_code == 201:
            contenido=response.content
            # print (contenido)
            # print (response.json())
            diccionario_respuesta=response.json()
            print(json.dumps(diccionario_respuesta, indent=4,sort_keys=True))

            self.token = diccionario_respuesta['data'][0]['token']
        except Exception as e:
            # Handle any exceptions that may occur during the process
            response = {
                'error' : False,
                'message': f'Error Ocurred: {e}',
                'data': None
            }
            print (json.dumps(response, indent=4, sort_keys=True))
    #Escribe en el socket mas controladamente.
    def escribe_socket(self, sock, datos):
        try:
            sock.send(datos.encode('utf-8'))
        except Exception as e:
            print("Error escribiendo en socket: ", e)

    #Lee del socket más controladamente
    def lee_socket(self, sock):
        try:
            p_datos = sock.recv(1024).decode('utf-8')
            return p_datos
        except Exception as e:
            print("Error leyendo el socket: ", e)
            return ""

    #Solicita unirse a la acción y espera una respuesta de un string que diga si ha sido aceptado
    #o denegado.
    def solicitar_inclusion(self, ip, puerto):
        aceptado = False

        try:
            cadena = f"{self.token} {self.id}"

            skcliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            skcliente.connect((ip, int(puerto)))

            self.escribe_socket(skcliente, cadena)

            inclusion = self.lee_socket(skcliente)

            dron = inclusion.split(" ")

            #Comprueba si el drone ha sido aceptado o no en el espectaculo
            if dron[0] == "aceptado":
                #print(self.id_virtual)
                self.id_virtual = int(dron[1])
                print("---Drone " + str(self.id_virtual) + " unido de manera satisfactoria---\n")
                aceptado = True
            else:
                print("---No se ha podido unir---\n")

            skcliente.close()
        except Exception as e:
            print("Error solicitando inclusion: " + str(e))

        return aceptado

#Ejecución normal del sitema drone. Lee los argumentos pasados al programa y los guarda en variables.
#Luego despliega un menú donde da la opción de registrarse, entrar al espectaculo o salir y cerrar el programa.
#Después de ser aceptado en el espectaculo se ejecuta el método run de la clase auxiliar UnirseAccion
#Al terminar la accion regresa al menu principal y puede volver a solicitar inclusion a la accion o salir.
if __name__ == "__main__":
    import sys
    #Comprueba el número de parametros importante
    if len(sys.argv) < 8:
        print("ERROR: No hay suficientes argumentos")
        print("$ ./AD_Drone.py alias ip_Engine puerto_Engine ip_Kafka puerto_Kafka ip_Registry puerto_Registry <id>")
        exit(-1)

    #Asigna los parametros
    drone = AD_Drone(sys.argv[1])
    ip_Engine = sys.argv[2]
    puerto_Engine = sys.argv[3]
    ip_Kafka = sys.argv[4]
    puerto_Kafka = sys.argv[5]
    ip_Registry = sys.argv[6]
    puerto_Registry = sys.argv[7]

    #SI hay un noveno paraametro lo asigno a la id del drone
    if len(sys.argv) == 9:
        if int(sys.argv[8]) == -1:
            drone.auto = True
        else:
            drone.id = int(sys.argv[8])

    #Menu principal
    opcion = -1

    broker = ip_Kafka + ":" + puerto_Kafka
    opcion_auto = 1
    while opcion != 3:
        print("[1] Registrar drone en el sistema")
        print("[2] Entrar al espectáculo")
        print("[3] Salir")

        if drone.auto == True:
            opcion = opcion_auto
            opcion_auto += 1
            print(opcion)
        else:
            opcion = int(input())

        if opcion == 1:
            drone.registrarse(ip_Registry, puerto_Registry)
        elif opcion == 2:
            aceptado = drone.solicitar_inclusion(ip_Engine, puerto_Engine)
            if aceptado:
                #Se une a la acción y realiza todas las operaciones kafka o que necesite para su funcionamiento
                drone.broker = broker
                drone.detener = False
                drone.run()
        else:
            exit(0)
