import sqlite3
import paho.mqtt.client as mqtt
from config import DB_NAME, MQTT_BROKER, MQTT_PORT, MQTT_TOPIC

# Tilaa MQTT brokerilta dataa ja tallenna se tietokantaan.