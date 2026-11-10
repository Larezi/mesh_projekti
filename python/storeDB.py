import sqlite3
import paho.mqtt.client as mqtt
from config import DB_NAME, MQTT_BROKER, MQTT_PORT, MQTT_TOPIC

#--- DATA BASE FUNCTIONS ---#
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            data TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def insert_data(data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sensor_data (data) VALUES (?)", (data,))
    conn.commit()
    conn.close()

#--- MQTT CALLBACK FUNCTIONS ---#
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Yhteys MQTT brokeriin muodostettu onnistuneesti.")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Yhteyden muodostaminen epäonnistui, koodi: {rc}")

def on_message(client, userdata, msg):
    try:
        data = msg.payload.decode('utf-8')
        if data:
            insert_data(data)
            print(f"Vastaanotettu ja tallennettu data: {data}")
    except Exception as e:
        print(f"Virhe datan vastaanottamisessa: {e}")

def main():
    init_db()

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_forever()
    except Exception as e:
        print(f"Yhteyden muodostaminen epäonnistui: {e}")

if __name__ == "__main__":
    main()
    