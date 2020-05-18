import datetime
import paho.mqtt.client as mqtt


def on_publish(client,userdata,result):    
#callback for publish to remote broker (Cloud)
    print("face published \n")
    pass

def on_connect_local(client, userdata, flags, rc):
#callback for connect to local broker (TX2)
    print("Connected to local broker")
    client.subscribe("hw3facestx2")	

def on_connect_remote(client, userdata, flags, rc):
#callback for connect to remote broker (Cloud)
    print("Connected to remote broker")

def on_message(client, userdata, msg):
#callback for message received from local broker (TX2)
    try:
	print("received face image locally")
	image = msg.payload
#on message received from local broker (TX2), publish to remote broker (Cloud)
	ret=remote_client.publish("hw3faces", image, qos=1)
	print(ret)
    except:
	print("Error reading", sys.exc_info()[0])


#Set up remote connection
remote_client = mqtt.Client("remote")
remote_client.on_publish = on_publish
remote_client.on_connect = on_connect_remote
remote_client.connect("52.116.5.178",1883, 60)
ret=remote_client.publish("hw3faces", "this is my test", qos=1)

#Set up local connection
local_client = mqtt.Client("local")
local_client.on_connect = on_connect_local
local_client.connect("172.17.0.1", 1883,60)
local_client.on_message = on_message

#Loop forever on local broker waiting for messages to forward
local_client.loop_forever()
