import cv2, time, pandas , keyboard
from threading import Thread
import multiprocessing
import os
import serial
import time, sys
import RPi.GPIO as GPIO
import smtplib, datetime, os, time
from gpiozero import LED,Button
from time import sleep
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime
import sqlite3
#define GPIO constants
detect_led = LED(27)
power_led  = LED(17)
button = Button(21)

power_led.on()    #turn power led on



#define variables....
thread_busy = 0
filename_ = ''
frame = 0
stop = 1
dr = "/var/www/html/pix/" 
dr_ = ''
tmmm = ''

NUMBER = ''
SUBJECT = ''
TEXT = ''
USERNAME = ''       # Username for authentication
PASSWORD = ''       # Password for authentication
FROM = ""  # Name shown as sender
TO = [] # Mail address of the recipient

SMTP_SERVER = 'smtp.gmail.com'  # URL of SMTP server
SSL_PORT = 465


#######################################################
#manage from sqli database 
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn
conn = get_db_connection()
sms = conn.execute('SELECT * FROM sms').fetchone()
emails = conn.execute('SELECT * FROM email').fetchall()
conn.close()
NUMBER = sms['phone']
for email in emails:
	TO.append(email['email'])

#########################################3#############
def tmm():
	mn = ''
	hr = ''
	global tmmm
	
	if ( (time.localtime(time.time()).tm_hour) < 10):
		hr = "0"+ str(time.localtime(time.time()).tm_hour)
	else:
		hr = str(time.localtime(time.time()).tm_hour)
	
	if ( (time.localtime(time.time()).tm_min) < 10):
		mn = "0"+ str(time.localtime(time.time()).tm_min)
	else:
		mn = str(time.localtime(time.time()).tm_min)
	tmmm = hr + ':' + mn
	print("time - " + tmmm)
	
###################################3###########3#######
def filename():
	mn = ''
	dy = ''
	global dr_
	if ( (time.localtime(time.time()).tm_mon) < 10):
		mn = "0"+ str(time.localtime(time.time()).tm_mon)
	else:
		mn = str(time.localtime(time.time()).tm_mon)
	
	if ( (time.localtime(time.time()).tm_mday) < 10):
		dy = "0"+ str(time.localtime(time.time()).tm_mday)
	else:
		dy = str(time.localtime(time.time()).tm_mday)
	filename_ = str(  int ( time.time() ) ) + ".jpg"  
	
	dr_ =  dr + filename_ 
	
#########################################3#############
thread_id = multiprocessing.Process(target=filename,args=())
button_id = multiprocessing.Process(target=filename,args=())
stopsend_id = multiprocessing.Process(target=filename,args=())
###################################3###########3#######
def filename1():
	mn = ''
	dy = ''
	global dr1_
	if ( (time.localtime(time.time()).tm_mon) < 10):
		mn = "0"+ str(time.localtime(time.time()).tm_mon)
	else:
		mn = str(time.localtime(time.time()).tm_mon)
	
	if ( (time.localtime(time.time()).tm_mday) < 10):
		dy = "0"+ str(time.localtime(time.time()).tm_mday)
	else:
		dy = str(time.localtime(time.time()).tm_mday)
	filename_ = str(  int ( time.time() ) + 1) + ".jpg"  
	dr1_ =  dr + filename_ 
	
##################################################################
def sendMail1(subject, text, img = None,img2 = None):
    global stop
    print("Sending Email to " + TO)
    msg = MIMEMultipart("alternative")
    msg.attach(MIMEText(text, "html"))

    tmpmsg = msg
    msg = MIMEMultipart()
    msg.attach(tmpmsg)
    if img != None:
        if not os.path.exists(img):
            print ("File", img, "does not exist." )
        else:
            fp = open(img, 'rb')
            img = MIMEImage(fp.read())  # included in mail, not as attachment
            fp.close()
            msg.attach(img)
    if img2 != None:
        if not os.path.exists(img2):
            print ("File", img2, "does not exist." )
        else:
            fp = open(img2, 'rb')
            img2 = MIMEImage(fp.read())  # included in mail, not as attachment
            fp.close()
            msg.attach(img2)
    
    msg['Subject'] = subject
    msg['From'] = FROM
    
    try:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SSL_PORT)
        print('1')
        server.login(USERNAME, PASSWORD)
        print('2')
        #sendmail is sending to a list , TO can be multiple emails
        server.sendmail(FROM, TO, msg.as_string())
        print('3')
    except:
        print('error sending mail')
        stop = 1
    else:
        server.quit()
        print("Mail successfully sent.")
        stop = 1
    os.system('sudo poff fona')
 
###############################################################################################
def  send_sms(tx,nm):
	print("sending sms :'"+ tx + " to: " + nm)
	SERIAL_PORT = "/dev/ttyAMA0"
	ser = serial.Serial(SERIAL_PORT, baudrate = 9600, timeout = 2)	
	tx = tx.replace(chr(10),"")
	nm = nm.replace(chr(10),"")
	ser.write(b'AT\n') 
	rcv = ser.read(30)
	print (str(rcv))
	time.sleep(1)	
	ser.write(b'AT+CMGF=1\n')  # Select Message format as Text mode
	time.sleep(2)
	rcv = ser.read(30)
	print (str(rcv))
	msgg = bytes( 'AT+CMGS="{}"\n'.format(nm),'utf-8')
	print(msgg)
	ser.write(msgg)
	time.sleep(3)
	rcv = ser.read(30)
	print (str(rcv))
	time.sleep(1)
	temp =( bytes('{}'.format(tx),'utf-8'))
	ser.write(temp)  # Message    
	temp = chr(26)
	ser.write( bytes('{}\n'.format(temp),'utf-8'))
	time.sleep(7)
	rcv = ser.read(50)
	if not rcv:
		print('nothing received ')
	else:
		print(rcv)
	if (b"CMTI" in rcv):
		print("sms sent")
	ser.close()
	time.sleep(5)

##############################################################################################
def  send_allert():
	text_ = TEXT + ' ('+ tmmm + ')hrs'   
	number_ = NUMBER 
	subject = "Intrusion detected."
	os.system('sudo pon fona')
	os.system('sudo python /home/pi/on1.py')
	sendMail1(SUBJECT, (subject + '@ '+ tmmm + ' hrs'), dr_,dr1_)   
	time.sleep(5)
	os.system('sudo poff fona')
	os.system('sudo poff fona')
	time.sleep(7)
	send_sms(text_,number_)
	thread_busy = 0
	print("--------------------------")
	detect_led.off()

def monitor_button():
	while  True:
		if button.is_pressed:
			#shutdown system
			os.system('sudo shutdown -h now')
			print("shutting down system...")
		time.sleep(0.5)


button_id = Thread(target=monitor_button,args=())
button_id.start()
thread_id = multiprocessing.Process(target=send_allert,args=())
#######################################################################
#      read back the settings from the  config1.dat file.


#######################################################################
#managing from database instead of files 
filepath = '/var/www/html/config1.dat'
fp = open(filepath,'r')
print('reading settings...')
if fp:
    USERNAME = fp.readline()
    PASSWORD = fp.readline()
    TO = fp.readline()


    FROM = fp.readline()       
    SUBJECT = fp.readline()
    TEXT = fp.readline()
    #NUMBER = fp.readline()
##########################################





print("Email Receipient = " + TO)
print("Subject = " + SUBJECT)
print("Sms Receipient=  " + NUMBER)
print("Sms message: " + TEXT)    
    

###################################
# Assigning our static_back to None
static_back = None

# Capturing video
video = cv2.VideoCapture(0)
time.sleep(3)   #wait for 3 seconds  to adjust camera brightness

check, frame = video.read()
count = 0
elapsed = 1

# Infinite while loop to treat stack of image as video
seconds_old = int( time.time() ) + elapsed    #calculate future 
while True:
	# Reading frame(image) from video
	time.sleep(0.1)	
	check, frame = video.read()
	seconds = int( time.time() )
	if (seconds_old <= seconds):
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		gray = cv2.GaussianBlur(gray, (21, 21), 0)
		static_back = gray
		seconds_old = int( time.time() ) + elapsed  # rewrite future time

	# Initializing motion = 0(no motion)
	motion = 0

	# Converting color image to gray_scale image
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

	# Converting gray scale image to GaussianBlur
	# so that change can be find easily
	gray = cv2.GaussianBlur(gray, (21, 21), 0)

	# In first iteration we assign the value
	# of static_back to our first frame
	if static_back is None:
		static_back = gray
		continue

	# Difference between static background
	# and current frame(which is GaussianBlur)
	diff_frame = cv2.absdiff(static_back, gray)

	# If change in between static background and
	# current frame is greater than 30 it will show white color(255)
	thresh_frame = cv2.threshold(diff_frame, 25, 255, cv2.THRESH_BINARY)[1]
	thresh_frame = cv2.dilate(thresh_frame, None, iterations = 2)

	# Finding contour of moving object
	cnts,_ = cv2.findContours(thresh_frame.copy(),
					cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	for contour in cnts:
		if cv2.contourArea(contour) < 3000:
			motion = 0
			continue
		motion = 1
		(x, y, w, h) = cv2.boundingRect(contour)
		# making green rectangle arround the moving object
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
       
	if (motion == 1):
		motion = 0
		detect_led.on()
		static_back = gray
		print("....Detected.....")
		tmm()
		
		if (not thread_id.is_alive()):
			os.system('sudo poff fona')
			filename()          #make filename
			cv2.imwrite( dr_ ,frame)
			time.sleep(1)   #pause and snap another
			check, frame = video.read()
			filename1()          #make filename
			cv2.imwrite( dr1_ ,frame)
			thread_busy = 1
			print("starting thread...")
			thread_id = multiprocessing.Process(target=send_allert,args=())
			thread_id.start()     #start the thead to do the sending
		else:
			print("*****thread busy********")
		
	key = cv2.waitKey(1)   # if q entered whole process will stop
	if key == ('q'):
		if motion == 1:
			pass 
		break
video.release()
cv2.destroyAllWindows()



