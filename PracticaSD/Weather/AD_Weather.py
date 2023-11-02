import socket
import sys
import time

class AD_Weather:
    def __init__(self):
        self.ciudades = []
        self.temperaturas = []

    def leer_socket(self, sock):
        try:
            datos = sock.recv(1024).decode('utf-8')
            return datos
        except Exception as e:
            print("Error:", e)
        return ""

    def escribe_socket(self, sock, p_datos):
        try:
            sock.send(p_datos.encode('utf-8'))
        except Exception as e:
            print("Error:", e)

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
            print(e)
        else:
            self.ciudades = ciudades_aux
            self.temperaturas = temperaturas_aux

    def clima_actual(self, ciudad):
        for i in range(len(self.ciudades)):
            if self.ciudades[i] == ciudad:
                return self.temperaturas[i]
        return -1.0

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

        clima = AD_Weather()

        conn, addr = s_socket.accept()
        while True:
            clima.actualizar_temperaturas()

            print("Esperando petición...")

            peticion = clima.leer_socket(conn)
            print(peticion)

            if len(peticion) > 0:
                temperatura = clima.clima_actual(peticion)

                print("Enviando temperatura en " + peticion + ": " + str(temperatura))
                clima.escribe_socket(conn, str(temperatura))
                if float(temperatura) <= 0.0:
                    print("CONDICIONES CLIMATICAS ADVERSAS.ESPECTACULO FINALIZADO")
                    break
            time.sleep(2)

        conn.close()
        s_socket.close()
    except Exception as e:
        print("Error:", e)
