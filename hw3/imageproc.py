import paho.mqtt.client as mqtt
import datetime



def on_connect_local(client, userdata, flags, rc):
    print("Connected to Broker")
    print(client)
    print(userdata)
    print(flags)
    print(rc)
    client.subscribe("hw3faces")


def on_message(client, userdata, msg):
    try:
       # print("face received ",image_num )
        print("face received")
        print(userdata)
        image = msg.payload
        currenttime=datetime.datetime.now()
        timestring=currenttime.strftime("%m-%d-%Y-%H:%M:%S")
        image_name = timestring + '.png'
        print(image_name)
        f = open(image_name, "x+b")
        f.write(image)
        f.close()
    except:
        print("error reading message", sys.exc_info()[0])
    pass

local_mqttclient = mqtt.Client()
local_mqttclient.on_connect = on_connect_local
local_mqttclient.connect("52.116.5.178",1883,60)
local_mqttclient.on_message = on_message

local_mqttclient.loop_forever()
