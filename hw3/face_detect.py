import numpy as np
import cv2
import datetime
import paho.mqtt.client as mqtt

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

def on_publish(client,userdata,result):             #create function for callback
    print("face published \n")
    pass

cap = cv2.VideoCapture(0)
cap.set(3,1920)
cap.set(4,1080)

while(True):
 # Capture frame-by-frame
    ret, frame = cap.read()
    print("frame captured")

    print frame.shape
 # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    cv2.imwrite('test.png', gray)
 # Display the resulting frame
    cv2.imshow('frame',gray)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x,y,w,h) in faces:
        print("face found")
        face = gray[y:y+h, x:x+w]
        currentTime = datetime.datetime.now()
        filename = str(currentTime.second) + '.png'
        print("saving local image")
        cv2.imwrite(filename,face)
        rc,png = cv2.imencode('.png', face)
	msg = png.tobytes()
	
        print("face publishing")

        client1= mqtt.Client("control2")                           #create client object
        client1.on_publish = on_publish                          #assign function to callback
#        client1.connect(broker,port)                                 #establish connection
        client1.connect("172.17.0.1",1883
                )                                 #establish connection
        ret= client1.publish("hw3facestx2",msg,qos=1)   




 # When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
