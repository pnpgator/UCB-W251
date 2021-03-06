import paho.mqtt.client as mqtt
import datetime


def on_connect_local(client, userdata, flags, rc):
#Connect to local broker (cloud)
    print("Connected to Broker")
    print(client)
    print(userdata)
    print(flags)
    print(rc)
    client.subscribe("hw3faces")


def on_message(client, userdata, msg):
#Callback for message received from local broker (cloud)
    try:
       # print("face received ",image_num )
        print("face received")
        print(userdata)
#Pull the message from payload
        image = msg.payload
#Create a unique filename to store the image
        currenttime=datetime.datetime.now()
        timestring=currenttime.strftime("%m-%d-%Y-%H:%M:%S")
        image_name = timestring + '.png'
        print(image_name)
#Store the face image locally (this script is running on the mounted drive)
        f = open(image_name, "x+b")
        f.write(image)
        f.close()
    except:
        print("error reading message", sys.exc_info()[0])
    pass


#Setup the local connection (cloud broker)
local_mqttclient = mqtt.Client()
local_mqttclient.on_connect = on_connect_local
local_mqttclient.connect("52.116.5.178",1883,60)
local_mqttclient.on_message = on_message

#loop forever waiting on messages coming from the local (cloud) broker
local_mqttclient.loop_forever()
