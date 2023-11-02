import time
import sys
import os

class Drone:
    def __init__(self, _id):
        self.id = _id
        self.coord_x = 0
        self.coord_y = 0
        self.pos_final = False

    def set_coordenada(self, x, y):
        self.coord_x = x
        self.coord_y = y

    def set_pos_final(self, pos_final):
        self.pos_final = pos_final


class Map:
    def __init__(self):
        self.filas = 19
        self.columnas = 19
        self.mapa = ""

    def get_filas(self):
        return self.filas

    def get_columnas(self):
        return self.columnas

    def print_mapa(self, drones, dronesActuales):
        rojo = "\u001B[91m"
        verde = "\u001B[32m"
        reset = "\u001B[0m"
        for i in range(0, 21):
            for j in range(0, 21):
                if i == 0:
                    if j == 0:
                        self.mapa += "     1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17  18  19  20 "
                elif j == 0:
                    if i < 10:
                        self.mapa += f" {i} "
                    else:
                        self.mapa += f"{i} "
                else:
                    for drone in drones:
                        droneFinal = []

                        #Encontrar posicion final del drone
                        for droneActual in dronesActuales:
                            if droneActual[0] == drone[0]:
                                droneFinal = droneActual

                        if drone[1][1] == i and drone[1][0] == j:
                            if drone[0] < 10:
                                if drone[1][0] == droneFinal[1][0] and drone[1][1] == droneFinal[1][1]:
                                    self.mapa += f"{verde} {drone[0]} {reset} "
                                else:
                                    self.mapa += f"{rojo} {drone[0]} {reset} "
                            else:
                                if drone[1][0] == droneFinal[1][0] and drone[1][1] == droneFinal[1][1]:
                                    self.mapa += f"{verde} {drone[0]} {reset} "
                                else:
                                    self.mapa += f"{rojo} {drone[0]} {reset} "
                        else:
                            self.mapa += "   "
                self.mapa += " "
            self.mapa += "\n"

    def to_string(self, drones, dronesActuales):
        if len(drones) == 0:
            drones = [[0, [-1, -1]]]
            
        self.mapa = ""
        sys.stdout.write("\b")
        self.print_mapa(drones, dronesActuales)
        return self.mapa

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

"""
if __name__ == "__main__":


    drones = [[1, [3, 4]], [2, [5, 5]], [3, [4, 2]], [4, [1, 2]]]

    dronesActuales = [[1, [3, 4]], [2, [5, 6]], [3, [4, 4]], [4, [1, 2]]]

    mapa = Map()

    clear_terminal()
    print(mapa.to_string(drones, dronesActuales))

    time.sleep(3)
    clear_terminal()

    drones[1][1][1] = 6


    print(mapa.to_string(drones, dronesActuales))
"""
