import paho.mqtt.client as mqtt
import json


# ============================================================
# MQTT SETTINGS
# ============================================================

BROKER = "broker.hivemq.com"
PORT = 8884

inTopic = "psna/robo/kit"
outTopic = "psna/robo/app"

received = ""


# ============================================================
# SEND COMMAND TO ROBOT
# ============================================================

def send(device, command):

    doc = {
        "device": device,
        "command": command
    }

    js = json.dumps(doc)

    print("MQTT SEND:", js)

    client.publish(outTopic, js)


# ============================================================
# MQTT CONNECT
# ============================================================

def on_connect(client, userdata, flags, rc):

    if rc == 0:
        print("MQTT connected successfully")

        client.subscribe(inTopic)

        print("Subscribed to:", inTopic)

    else:
        print("MQTT connection failed. Code:", rc)


# ============================================================
# MQTT RECEIVE
# ============================================================

def on_message(client, userdata, msg):

    global received

    received = msg.payload.decode()

    print(
        "MQTT RECEIVE:",
        msg.topic,
        received
    )


# ============================================================
# CREATE MQTT CLIENT
# ============================================================

client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message


# ============================================================
# CONNECT
# ============================================================

print("Connecting to MQTT broker...")

client.connect(
    BROKER,
    PORT,
    120
)


# ============================================================
# START MQTT NETWORK LOOP
# ============================================================

client.loop_start()

print("MQTT system ready")