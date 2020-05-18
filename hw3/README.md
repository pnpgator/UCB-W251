# UCB W251 Deep Learning in the Cloud and at the Edge

# Homework 3 - Pritesh Patel

## Introduction

This writeup covers the work I performed in accomplishing the Homework 3 assignment.

The write up discusses my approach to creating each stage in the pipeline shown below:

![this](hw03.png)

I will start at the bottom of the architecture at the USB cam and work up to the cloud storage.

## Face detector

In order to get started I wrote a script that ran on the host machine (TX2) natively. This allowed me to work out basic coding issues without dealing with any Docker challenges. I ran into some challenges getting the images from the capture and then cutting the faces. I ended up saving the images both pre crop and post crop locally to test this part out. I also added the MQTT client and made sure I could get the end to end flow working. After I did get the end to end flow working I moved my implentation of the face detector to a Docker container.
 
I created a base image leveraging the Yolo Dockerfile provided in week1. I started and ran the container using
```
docker run -e DISPLAY=$DISPLAY --rm  --network hw03 --privileged -v /tmp:/tmp -ti yolo
```

In particular I wanted to ensure the container ran in privileged mode to gain access to the camera and also that it connected to the bridge network that was created as part of the homework instructions.

In order to get the environment I needed for my script to run I installed python-pip and then pip installed numpy and paho-mqtt. 

I also copied the Haar Cascade classifier XML and the face_detect.py script.
```
sudo docker cp host_source_path <container_id>:dest_path
```

I wrote the face_detect.py script to capture the camera frames, detect the faces and crop the image to the dimension of the face as detected by the HAAR Cascade classifier. The same script then pushes the cropped face image to the local MQTT broker using the "hw3facestx2" topic. That topic name was chosen to distinguish it from the topic name used by the cloud broker.
I used qos=1 to make sure that the broker ensures the message gets delivered atleast once. 

I did run into one issue moving the script to the container. For some reason the OpenCV camera capture defaulted to a lower resolution in the container than when run directly on the host. I ended up finding settings to allow the script to capture high res from within the container.

```
cap.set(3,1920)
cap.set(4,1080)
```

Besides that, I tried for a bit to make a Dockerfile to create the full environment I wanted but ran out of time. I am likely to do that anyway just to prove it works as I expect it should. I think its simply a matter of adding the python-pip and pip install commands in the Dockerfile. I suspect I can remove some of the Yolo and Darknet lines but now that I have this working, I will wait until after this HW is graded. 


## Mosquitto on Alpine

This was pretty simple. I just needed to run:
```
docker run --name mosquitto --network hw03 -p 1883:1883 -ti alpine sh

#from inside the container install the mosquitto package and run it
apk update
apk add mosquitto
run mosquitto
```
I left this window up so I could see the output from this container as clients connected and disconnected.


## Forwarder

I started the forwarder as instructed in the HW instructions
```
docker run --name forwarder --network hw03 -ti alpine sh
apk update
apk add mosquitto-clients
```

Initially I used the command line to subscribe and publish to test this out but then wrote the forwarder.py script to accomplish this stage of the pipeline. 

The forwarder script connects to the local broker on the TX2 and the remote broker on the IBM Cloud and passes the messages (in this case png images) from TX2 to IBM Cloud. I included some debug messages in the forwarder to make sure images were coming in and leaving. 


## Cloud MQTT Broker

The cloud MQTT broker was run as a container in the cloud VSI. 
The cloud side of the MQTT Broker was also pretty simple. I created a container on my VSI using the same command line I used for the one on the TX2. So this created a Mosquitto Broker on the cloud side using Alpine Linux. I just needed to make sure I understood how to reach this broker which was as simple as using the VSI IP address and port binding 1883 through the docker run command:
```
docker run --name mosquitto -p 1883:1883 -ti alpine sh
```

For the cloud side messages were passed using the topic hw3faces versus hw3facestx2 that was used on the Jetson TX2. 

In order to test this out, I sent text messages on the hw3faces topic to make sure they reached the right cloud broker instance. This was then extended to make sure those messages were received and stored in the Cloud Object Storage by the Image Processor container.


## Image Processor

The final stage in the pipeline involved taking the messages from the cloud MQTT broker and storing them off onto IBM Cloud Object Storage. After completing the cloud storage lab I already had cloud storage mounted on the VSI. So the key was to expose that mount to the container. This was done using:
```
docker run -v /mnt/mybucket:/mnt/mybucket --name imageprocessor -ti ubuntu bash
```
Now I could save files in the container in /mnt/mybucket and they would automatically get synced to my Cloud Object Storage [Link to Cloud Storage](https://cloud.ibm.com/objectstorage/crn%3Av1%3Abluemix%3Apublic%3Acloud-object-storage%3Aglobal%3Aa%2F2a62d5fa62a547508fdff9b8f5a93b50%3A0566f5f6-35be-4e30-949c-8e88fbef6794%3A%3A?bucket=priteshnpatel-bucket1&bucketRegion=us-east&endpoint=s3.us-east.cloud-object-storage.appdomain.cloud&paneId=bucket_overview)

I wrote the ImageProc.py script to take the messages from the hwfaces topic of the Cloud MQTT Broker and save them as objects in Cloud Object Storage. The challenge here was creating new file names for each image so I used the date and time to name the files. This was the date and time of the image reception by the ImageProc script versus the date and time of the original capture. 

The ImageProc.py script actually ran from /mnt/mybucket so it could save the images in its home directory and they would automatically get stored in the Cloud Object Storage. This also means that the script itself was also stored in Cloud Object Storage so could easily be ported across container instances. This saved having to copy the script back in if I had to get rid of a container instance and start it up again.


## Summary

I successfully built all 5 stages of this pipeline and ran the operational system a couple of times. There are several different images in the cloud storage as well as some of the test text messages I used for debugging. The face detector could be improved to select which images to send better. I'm sure there are enhnacements that can be done there. All in all, I was happy with the results given the limited time I had to work on it. 

This was a challenging project in that there were many times that I got stuck and struggled to understand what I needed to do or how to fix an issue I was running into. In retrospect this was not that hard now that I understand what I needed to do get it all working, but the journey itself took time and a lot of trial and error, troubleshooting, research, asking folks on Slack...etc. I also noticed that the order of starting up the services mattered. I would start both the brokers first, then the forwarder and image processor and finally the face detector. Sometimes if the order was different the clients would not connect or messages would not flow as expected. Now that I have this pipeline working I could use the top 4 components for many different usecases and probably easily extend them to serve multiple use cases simulataneously. The difference really comes down to changing the face detector to collect other types of information or do additional processing. I look forward to leveraging this architecture in the future.
