#!/bin/bash

ip_broker=192.168.0.35
puerto_broker=9092
ip_clima=192.168.0.35
puerto_clima=8085
ciudad=Alicante
max_drones=6

gnome-terminal -- bash -c "python3 AD_Engine.py 9090 $max_drones $ip_broker:$puerto_broker $ip_clima:$puerto_clima $ciudad; exec bash"
gnome-terminal -- bash -c "python3 AD_Registry.py 8081; exec bash"
