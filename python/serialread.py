import serial
import time
import paho.mqtt.client as mqtt
from config import SERIAL_PORT, BAUD_RATE, MQTT_BROKER, MQTT_PORT, MQTT_TOPIC

# Lukee sarjaportista dataa ja muokkaasen käytettävään muotoon.
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

line = ser.readline()
text = line.decode('utf-8').strip()
print(f"Luettu data: {text}") #Debug: tulostaa luetun datan konsoliin.

# Julkaisee luetun datan MQTT brokerille.