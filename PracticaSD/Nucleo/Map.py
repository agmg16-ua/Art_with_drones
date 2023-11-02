import time
import sys
import os
import AD_Engine

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

    def print_mapa(self, drones):
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
                    existe = False
                    for drone in drones:
                        if drone.coord_y == i and drone.coord_x == j:
                            existe = True
                            if drone.id < 10:
                                if drone.pos_final:
                                    self.mapa += f"{verde} {drone.id} {reset} "
                                else:
                                    self.mapa += f"{rojo} {drone.id} {reset} "
                            else:
                                if drone.pos_final:
                                    self.mapa += f"{verde} {drone.id} {reset} "
                                else:
                                    self.mapa += f"{rojo} {drone.id} {reset} "
                    if not existe:
                        self.mapa += "   "
                self.mapa += " "
            self.mapa += "\n\n"

    def to_string(self, drones):
        self.mapa = ""
        sys.stdout.write("\b")
        self.print_mapa(drones)
        return self.mapa


def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

"""
if __name__ == "__main__":
    drone1 = Drone(1)
    drone1.set_coordenada(8, 5)
    drone2 = Drone(2)
    drone2.set_coordenada(5, 8)
    drone2.set_pos_final(True)
    drone3 = Drone(3)
    drone3.set_coordenada(10, 10)
    drone4 = Drone(4)
    drone4.set_coordenada(15, 15)
    drone5 = Drone(5)
    drone5.set_coordenada(9, 11)
    drone5.set_pos_final(True)
    drone6 = Drone(6)
    drone6.set_coordenada(11, 9)
    drone7 = Drone(7)
    drone7.set_coordenada(4, 1)
    drone8 = Drone(8)
    drone8.set_coordenada(1, 4)
    drone8.set_pos_final(True)
    drone9 = Drone(9)
    drone9.set_coordenada(9, 9)
    drone10 = Drone(10)
    drone10.set_coordenada(10, 10)

    drones = [drone1, drone2, drone3, drone4, drone5, drone6, drone7, drone8, drone9, drone10]

    mapa = Map()

    print(mapa.to_string(drones))

    time.sleep(3)
    clear_terminal()

    drone1.set_pos_final(True)
    drone7.set_pos_final(True)
    drone9.set_pos_final(True)
    drone3.set_pos_final(True)


    print(mapa.to_string(drones))
"""
