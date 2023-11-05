import socket
import sys
import time
import threading

class EscucharEngine(threading.Thread):
    def __init__(self, skEngine):
        super().__init__()
        self.engine = skEngine
        self.ciudades = []
        self.temperaturas = []

    def leer_socket(self, sock):
        try:
            datos = sock.recv(1024).decode('utf-8')
            return datos
        except Exception as e:
            print("Error al leer datos del socket:", e)
        return ""

    def escribe_socket(self, sock, p_datos):
        try:
            sock.send(p_datos.encode('utf-8'))
        except Exception as e:
            print("Error al enviar datos socket: ", e)

    def actualizar_temperaturas(self):
        ciudades_aux = []
        temperaturas_aux = []

        try:
            with open("climas.txt", "r") as archivo:
                for linea in archivo:
                    partes = linea.split(" ")
                    if len(partes) == 2:
                        ciudad = partes[0]
                        temperatura = float(partes[1])
                        ciudades_aux.append(ciudad)
                        temperaturas_aux.append(temperatura)

        except Exception as e:
            print("Error al abrir la base de datos de climas: ", e)
        else:
            self.ciudades = ciudades_aux
            self.temperaturas = temperaturas_aux

    def clima_actual(self, ciudad):
        for i in range(len(self.ciudades)):
            if self.ciudades[i] == ciudad:
                return self.temperaturas[i]
        return -1.0

    def run(self):
        while True:
            self.actualizar_temperaturas()

            print("Esperando petición...")

            peticion = self.leer_socket(conn)
            print(peticion)

            if len(peticion) > 0:
                temperatura = self.clima_actual(peticion)

                print("Enviando temperatura en " + peticion + ": " + str(temperatura))
                self.escribe_socket(conn, str(temperatura))
                if float(temperatura) <= 0.0:
                    print("CONDICIONES CLIMATICAS ADVERSAS.ESPECTACULO FINALIZADO")
                    break
            time.sleep(2)
        self.engine.close()


if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            print("Especifica el puerto de escucha")
            sys.exit(1)

        puerto = int(sys.argv[1])

        # Obtiene la dirección IP local de la red actual
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()

        # Creo el servidor a la espera de drones que me llamen por ahí
        s_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s_socket.bind((local_ip, puerto))
        s_socket.listen()

        while True:
            conn, addr = s_socket.accept()
            try:
                escuchar = EscucharEngine(conn)
                escuchar.start()
            except Exception as e:
                print("Error para escuchar al engine: ", e)

    except Exception as e:
        print("Error al crear el servidor del clima:", e)
