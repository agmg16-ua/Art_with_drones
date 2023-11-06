#!/bin/bash

ip_engine=192.168.0.35
ip_broker=192.168.0.35
ip_registry=192.168.0.35
tiempo=5

gnome-terminal -- bash -c "python3 AD_Drone.py drone1 $ip_engine 9090 $ip_broker 9092 $ip_registry 8081; exec bash"
sleep $tiempo
gnome-terminal -- bash -c "python3 AD_Drone.py drone2 $ip_engine 9090 $ip_broker 9092 $ip_registry 8081; exec bash"
sleep $tiempo
gnome-terminal -- bash -c "python3 AD_Drone.py drone3 $ip_engine 9090 $ip_broker 9092 $ip_registry 8081; exec bash"
sleep $tiempo
gnome-terminal -- bash -c "python3 AD_Drone.py drone4 $ip_engine 9090 $ip_broker 9092 $ip_registry 8081; exec bash"
sleep $tiempo
gnome-terminal -- bash -c "python3 AD_Drone.py drone5 $ip_engine 9090 $ip_broker 9092 $ip_registry 8081; exec bash"
sleep $tiempo
gnome-terminal -- bash -c "python3 AD_Drone.py drone6 $ip_engine 9090 $ip_broker 9092 $ip_registry 8081; exec bash"
sleep $tiempo
gnome-terminal -- bash -c "python3 AD_Drone.py drone7 $ip_engine 9090 $ip_broker 9092 $ip_registry 8081; exec bash"
sleep $tiempo
gnome-terminal -- bash -c "python3 AD_Drone.py drone8 $ip_engine 9090 $ip_broker 9092 $ip_registry 8081; exec bash"
sleep $tiempo
gnome-terminal -- bash -c "python3 AD_Drone.py drone9 $ip_engine 9090 $ip_broker 9092 $ip_registry 8081; exec bash"
sleep $tiempo
gnome-terminal -- bash -c "python3 AD_Drone.py drone10 $ip_engine 9090 $ip_broker 9092 $ip_registry 8081; exec bash"
sleep $tiempo
gnome-terminal -- bash -c "python3 AD_Drone.py drone11 $ip_engine 9090 $ip_broker 9092 $ip_registry 8081; exec bash"
sleep $tiempo
gnome-terminal -- bash -c "python3 AD_Drone.py drone12 $ip_engine 9090 $ip_broker 9092 $ip_registry 8081; exec bash"
sleep $tiempo
gnome-terminal -- bash -c "python3 AD_Drone.py drone13 $ip_engine 9090 $ip_broker 9092 $ip_registry 8081; exec bash"
sleep $tiempo
gnome-terminal -- bash -c "python3 AD_Drone.py drone14 $ip_engine 9090 $ip_broker 9092 $ip_registry 8081; exec bash"
sleep $tiempo
gnome-terminal -- bash -c "python3 AD_Drone.py drone15 $ip_engine 9090 $ip_broker 9092 $ip_registry 8081; exec bash"
sleep $tiempo
gnome-terminal -- bash -c "python3 AD_Drone.py drone16 $ip_engine 9090 $ip_broker 9092 $ip_registry 8081; exec bash"
sleep $tiempo
gnome-terminal -- bash -c "python3 AD_Drone.py drone17 $ip_engine 9090 $ip_broker 9092 $ip_registry 8081; exec bash"
sleep $tiempo
gnome-terminal -- bash -c "python3 AD_Drone.py drone18 $ip_engine 9090 $ip_broker 9092 $ip_registry 8081; exec bash"
sleep $tiempo
gnome-terminal -- bash -c "python3 AD_Drone.py drone19 $ip_engine 9090 $ip_broker 9092 $ip_registry 8081; exec bash"
sleep $tiempo
gnome-terminal -- bash -c "python3 AD_Drone.py drone20 $ip_engine 9090 $ip_broker 9092 $ip_registry 8081; exec bash"
sleep $tiempo
