#!/bin/bash

ip_engine=192.168.0.35
ip_broker=192.168.0.35
ip_registry=192.168.0.35

gnome-terminal -- bash -c "python3 AD_Drone.py drone1 $ip_engine 9090 $ip_broker 9092 $ip_registry 8081; exec bash"
sleep 10
gnome-terminal -- bash -c "python3 AD_Drone.py drone2 $ip_engine 9090 $ip_broker 9092 $ip_registry 8081; exec bash"
sleep 10
gnome-terminal -- bash -c "python3 AD_Drone.py drone3 $ip_engine 9090 $ip_broker 9092 $ip_registry 8081; exec bash"
sleep 10
gnome-terminal -- bash -c "python3 AD_Drone.py drone4 $ip_engine 9090 $ip_broker 9092 $ip_registry 8081; exec bash"
sleep 10
gnome-terminal -- bash -c "python3 AD_Drone.py drone5 $ip_engine 9090 $ip_broker 9092 $ip_registry 8081; exec bash"
sleep 10
gnome-terminal -- bash -c "python3 AD_Drone.py drone6 $ip_engine 9090 $ip_broker 9092 $ip_registry 8081; exec bash"
sleep 10
gnome-terminal -- bash -c "python3 AD_Drone.py drone7 $ip_engine 9090 $ip_broker 9092 $ip_registry 8081; exec bash"
sleep 10
gnome-terminal -- bash -c "python3 AD_Drone.py drone8 $ip_engine 9090 $ip_broker 9092 $ip_registry 8081; exec bash"
