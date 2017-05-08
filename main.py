#required libraries
import sys
import ssl
import requests
import json
import paho.mqtt.client as mqtt
import config

#called while client tries to establish connection with the server
def on_connect(mqttc, obj, flags, rc):
    if rc==0:
        print ("Subscriber Connection status code: "+str(rc)+" | Connection status: successful")
    elif rc==1:
        print ("Subscriber Connection status code: "+str(rc)+" | Connection status: Connection refused")

#called when a topic is successfully subscribed to
def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos)+"data"+str(obj))

#called when a message is received by a topic
def on_message(mqttc, obj, msg):
    print("Received message from topic: "+msg.topic+"\n | QoS: "+str(msg.qos)+"\n | Data Received: "+str(msg.payload)) + "\n"
    data = json.loads(msg.payload)
    if data["state"]["desired"]["ops"] == "LightOn":
        print "light on"
        with open("/sys/class/leds/user/brightness", "w") as f:
            f.write('1')
    elif data["state"]["desired"]["ops"] == "LightOff":
        print "light off"
        with open("/sys/class/leds/user/brightness", "w") as f:
            f.write('0')

#creating a client with client-id=mqtt-test
mqttc = mqtt.Client(client_id="mqtt-MYS-6ULX")

mqttc.on_connect = on_connect
mqttc.on_subscribe = on_subscribe
mqttc.on_message = on_message

#Configure network encryption and authentication options. Enables SSL/TLS support.
#adding client-side certificates and enabling tlsv1.2 support as required by aws-iot service
mqttc.tls_set(config.certRootFile,
                certfile=config.certFile,
                keyfile=config.certPrivateFile,
              tls_version=ssl.PROTOCOL_TLSv1_2,
              ciphers=None)

#connecting to aws-account-specific-iot-endpoint
mqttc.connect(config.AWSIoTEndPoint, port=8883) #AWS IoT service hostname and portno

#the topic to publish to
mqttc.subscribe("$aws/things/" + config.AWSIoT_ID + "/shadow/update") #The names of these topics start with $aws/things/thingName/shadow."

#automatically handles reconnecting
mqttc.loop_forever()
