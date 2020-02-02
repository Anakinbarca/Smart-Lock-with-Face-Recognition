import sys
from Adafruit_IO import MQTTClient
import cv2
import numpy as np
import os 
import time
from time import perf_counter
import requests
from datetime import datetime
import csv

ADAFRUIT_IO_KEY = 'aio_iWuf98LvGuVwISyCvo2PSXtB6sbc'
ADAFRUIT_IO_USERNAME = 'Anakinbarca'
FEED_ID = 'DoorChecker'
IFTTTWEBHOOKS="I27ZBj7-UuG5kSZQGKbQLnO7Z7ZwpFbU7iOZ8Hpcd2"
CAMERAIP="192.168.1.30"

#global checkTheDoor
checkTheDoor = True
MoveSensor=True
DoorSensor=True
now = datetime.now()
dt_string = now.strftime("%d-%m-%Y %H-%M-%S")

def actuator():
    


    servo = 22
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(servo,GPIO.OUT)
    p=GPIO.PWM(servo,50)# 50hz frequency
    p.start(7.5)
    cnt=0
    try:
        while cnt<4:
            p.ChangeDutyCycle(12.5)
            time.sleep(1)
            p.ChangeDutyCycle(7.5)
            time.sleep(1)
            p.ChangeDutyCycle(2.5)
            time.sleep(1)
            cnt=cnt+2
           
    except KeyboardInterrupt:
        GPIO.cleanup()

def trigger(folder,value1):
    
    photoFile="log/"+ folder +"/Photo"+ str(dt_string) +".jpg"
    cv2.imwrite(photoFile, img)
    requests.post('https://maker.ifttt.com/trigger/Door_Open/with/key/'+IFTTTWEBHOOKS, params={"value1":value1,"value2":dt_string,"value3":"none"})
    print("\n [INFO] Exiting Program and cleanup stuff")
    return photoFile,dt_string
    cam.release()
    #cv2.destroyAllWindows()
    cv2.destroyWindow(cam)
    
    
def secTrigger(value1):
    requests.post('https://maker.ifttt.com/trigger/Security_Question/with/key/'+IFTTTWEBHOOKS, params={"value1":value1,"value2":dt_string,"value3":"none"})
    print("\n [INFO] Exiting Program and cleanup stuff")
    cam.release()
    cv2.destroyAllWindows()
    
def write_to_csv(photoFile,dt_string,name):
    with open("log/log_Files.csv", mode="a") as csv_readings:
        logfile_write = csv.writer(csv_readings, delimiter=",", quotechar="/""", quoting=csv.QUOTE_MINIMAL)
        write_to_log = logfile_write.writerow([photoFile,dt_string,name])
    return(write_to_log)
    
def openDoor():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('trainer/trainer.yml')
    cascadePath = "Cascades/haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascadePath);

    font = cv2.FONT_HERSHEY_SIMPLEX

    doorIsOpen=False
    batsoi=False
    #iniciate id counter
    id = 0
    cnt=0
    cnt2=0
    # names related to ids: example ==> Marcelo: id=1,  etc
    names = ['None', 'Thanos','Giannis'] 

    # Initialize and start realtime video capture
    cam = cv2.VideoCapture("rtsp://"+CAMERAIP+":8080/h264_pcm.sdp")
    cam.set(3, 640) # set video widht
    cam.set(4, 480) # set video height

    # Define min window size to be recognized as a face
    minW = 0.1*cam.get(3)
    minH = 0.1*cam.get(4)

    while True:
        ret, img =cam.read()
        img = cv2.flip(img, 0) # Flip vertically
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        
        faces = faceCascade.detectMultiScale( 
            gray,
            scaleFactor = 1.2,
            minNeighbors = 5,
            minSize = (int(minW), int(minH)),
           )
        
        for(x,y,w,h) in faces:
            cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
            id, confidence = recognizer.predict(gray[y:y+h,x:x+w])
            # Check if confidence is less them 100 ==> "0" is perfect match 
            if (confidence < 100):
                id = names[id]
                confidence = "  {0}%".format(round(100 - confidence))
                cnt=cnt+1;
                if cnt%5==0:
                    doorIsOpen=True
                    photoFile,dt_string= trigger("Success","Anoi3e h porta!!!!")
                    write_to_csv(photoFile,dt_string,str(id))
                    return doorIsOpen,batsoi
            else:
                id = "unknown"
                confidence = "  {0}%".format(round(100 - confidence))
                cnt=cnt+1;
                if cnt%50==0:
                    batsoi=True
                    photoFile,dt_string=trigger("Fail","Prospa8eia paravasiasis erxontai oi mpatsoi!!")
                    write_to_csv(photoFile,dt_string,str(id))
                    return doorIsOpen,batsoi
        
            cv2.putText(img, str(id), (x+5,y-5), font, 1, (255,255,255), 2)
            cv2.putText(img, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)  
    
        cv2.imshow('camera',img) 

        k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
        if k == 27:
            break
        
    return doorIsOpen,batsoi
    # Do a bit of cleanup
    print("\n [INFO] Exiting Program and cleanup stuff")
    cam.release()
    cv2.destroyAllWindows()
    
def connected(client):

    print('Connected to Adafruit IO!  Listening for {0} changes...'.format(FEED_ID))
    client.subscribe(FEED_ID)

def subscribe(client, userdata, mid, granted_qos):
    print('Subscribed to {0} with QoS {1}'.format(FEED_ID, granted_qos[0]))

def disconnected(client):
    print('Disconnected from Adafruit IO!')
    sys.exit(1)

def message(client, feed_id, payload):
    if payload=="IsDoorOpen":
        if checkTheDoor == False:
            print("sendtoIFTTT porta kleisth")
            requests.post('https://maker.ifttt.com/trigger/CheckCondDoor/with/key/'+IFTTTWEBHOOKS, params={"value1":"Closed","value2":dt_string,"value3":"none"})
            print(checkTheDoor)

        else:
            print("send to IFTTT porta anoixth")
            requests.post('https://maker.ifttt.com/trigger/CheckCondDoor/with/key/'+IFTTTWEBHOOKS, params={"value1":"Open","value2":dt_string,"value3":"none"})
            print(checkTheDoor)
    
    elif payload =="FaceRec":
        print("Face Recognition Mode")
        isDoorOpen,batsoi = openDoor()
        if isDoorOpen==True:
            print('ANOI3E H PORTA')
            print(isDoorOpen,batsoi)
        elif batsoi==True:
            print('FONA3E TOUS MPATSOUS')
            print(isDoorOpen)
            
    elif payload=="SensorSection":
        print("Let's control Sensors")
        if checkTheDoor==True and MoveSensor==False:
            print("Close the door. IFTT kai actuator")
			actuator()
        elif checkTheDoor==True and MoveSensor==True:
            print("Somebody left the door open. Do you want to close it?")
            doorQuest = input('Do you want to Close the door?[y/n]')
            if doorQuest=='y':
                #checkTheDoor=False
                print("The door is now closed")
                actuator()
				GPIO.cleanup()
            else:
                print("Not an option")
        elif checkTheDoor==False and DoorSensor==True:
            print("Perimenoume 3 sec gia na doume an einai akoma ekei")
            time.sleep(3)
            if DoorSensor == True:
                print("Mallon exeis gemata xeria. Anoigei h porta.")
                #checkTheDoor=True
				actuator()
				GPIO.cleanup()
            else:
                print("Efyge mprosta apo thn porta. 8a parameinei kleisth")
        else:
            print("Everything works great")
	
	elif payload=="OpenTheDoor":
		if checkTheDoor == False:
            print("The door is opening")
			requests.post('https://maker.ifttt.com/trigger/OpenPush/with/key/'+IFTTTWEBHOOKS, params={"value1":"Open","value2":"value2","value3":"none"})

            actuator()
			GPIO.cleanup()
        else:
		print("Door is already Open")
	
	elif payload=="CloseTheDoor":
		if checkTheDoor == True:
            print("The door is locking now")
			requests.post('https://maker.ifttt.com/trigger/ClosePush/with/key/'+IFTTTWEBHOOKS, params={"value1":"Open","value2":"value2","value3":"none"})
            actuator()
			GPIO.cleanup()
        else:
		print("Door is already Closed")


client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

client.on_connect    = connected
client.on_disconnect = disconnected
client.on_message    = message
client.on_subscribe  = subscribe

client.connect()

client.loop_blocking()
