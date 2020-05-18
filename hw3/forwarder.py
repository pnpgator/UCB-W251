import datetime
import paho.mqtt.client as mqtt


def on_publish(client,userdata,result):             #create function for callback
    print("face published \n")
    pass

def on_connect_local(client, userdata, flags, rc):
    print("Connected to local broker")
    client.subscribe("hw3facestx2")	

def on_connect_remote(client, userdata, flags, rc):
    print("Connected to remote broker")

def on_message(client, userdata, msg):
    try:
	print("received face image locally")
	image = msg.payload
	ret=remote_client.publish("hw3faces", image, qos=1)
	print(ret)
    except:
	print("Error reading", sys.exc_info()[0])



remote_client = mqtt.Client("remote")
remote_client.on_publish = on_publish
remote_client.on_connect = on_connect_remote
remote_client.connect("52.116.5.178",1883, 60)
ret=remote_client.publish("hw3faces", "this is my test", qos=1)

local_client = mqtt.Client("local")
local_client.on_connect = on_connect_local
local_client.connect("172.17.0.1", 1883,60)
local_client.on_message = on_message

local_client.loop_forever()
