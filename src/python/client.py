from paho.mqtt import client as mqtt_client
import random
import time

broker="localhost"
topic="test"
x=0
port = 1883

# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'

def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Conectado al MQTT Broker!")
        else:
            print("Erro al conectar al MQTT Broker %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish(client):
    msg_count = 0
    for x in range(5):
        time.sleep(1)
        msg = f"Mensaje: {msg_count}"
        result = client.publish(topic, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Se envio ({msg}) al topic ({topic})")
        else:
            print(f"Error al enviar el mensaje al topic ({topic})")
        msg_count += 1

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Recibido ({msg.payload.decode()}) del topic ({msg.topic})")

    client.subscribe(topic)
    client.on_message = on_message

def run():
    client = connect_mqtt()
    subscribe(client)
    publish(client)
    client.loop_forever()

if __name__ == '__main__':
    run()