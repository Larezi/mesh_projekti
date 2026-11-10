import serial
import time
import paho.mqtt.client as mqtt
from config import SERIAL_PORT, BAUD_RATE, MQTT_BROKER, MQTT_PORT, MQTT_TOPIC

def main ():
    # Muodostaa yhteydet MQTT brokeriin
    client = mqtt.Client()
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        print(f"Yhteys MQTT brokeriin:{MQTT_BROKER}:{MQTT_PORT} muodostettu.")
    except Exception as e:
        print(f"Yhteyden muodostaminen epäonnistui: {e}")
        return

    # Muodostaa yhteyden sarjaporttiin
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Lukee dataa sarjaportista {SERIAL_PORT}...")
    except Exception as e:
        print(f"Sarjaportin yhteyden muodostaminen epäonnistui: {e}")
        client.loop_stop()
        return

    # Lukee dataa sarjaportista ja julkaisee sen MQTT brokeriin
    while True:
        try:
            if ser.in_waiting > 0:
                data = ser.readline().decode('utf-8', errors='ignore').strip()
                if data:
                    client.publish(MQTT_TOPIC, data)
                    print(f"Julkaistu data: {data}")
        except KeyboardInterrupt:
            print("Pysäytetään ohjelma")
            ser.close()
            client.loop_stop()
            break
        except Exception as e:
            print(f"Virhe datan lukemisessa tai julkaisemisessa: {e}")

if __name__ == "__main__":
    main()