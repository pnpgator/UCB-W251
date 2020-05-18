import numpy as np
import cv2
import datetime
import paho.mqtt.client as mqtt

#Pull in the face classifier
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

def on_publish(client,userdata,result):    #create function for publish callback
    print("face published \n")
    pass

cap = cv2.VideoCapture(0)
cap.set(3,1920)
cap.set(4,1080)

while(True):
 # Capture frame-by-frame
    ret, frame = cap.read()
    print("frame captured")

 # grayscale to save memory 
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
 # print out frame capture to see pre and post crop image
    cv2.imwrite('test.png', gray)

 # Display the resulting frame
    cv2.imshow('frame',gray)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


 # Detect the faces in the resulting frame
    
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

 # For each detected face
    for (x,y,w,h) in faces:
        print("face found")
 # Crop the image to just the face
        face = gray[y:y+h, x:x+w]
 # Save the face image locally for troubleshooting 
        currentTime = datetime.datetime.now()
        filename = str(currentTime.second) + '.png'
        print("saving local image")
        cv2.imwrite(filename,face)
 # Encode the face image for sending
        rc,png = cv2.imencode('.png', face)
	msg = png.tobytes()
	
 # Publish the face image to the broker
        print("face publishing")
        client1= mqtt.Client("control2")           #create client object
        client1.on_publish = on_publish            #assign function to callback
        client1.connect("172.17.0.1",1883
                )                                 #establish connection
        ret= client1.publish("hw3facestx2",msg,qos=1)   


 # When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
