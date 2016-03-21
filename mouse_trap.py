#!/usr/bin/python
#===========================================================================
# mouse_trap.py
#
#
# 2016-03-04
# Carter Nelson
#===========================================================================
import RPi.GPIO as IO
import picamera
import Image, ImageDraw, ImageFont
import io
import random
from datetime import datetime
from time import sleep

# setup GPIO
PIR_PIN = 25
MTR_PWR_PIN = 23
MTR_CTL_PIN = 22
LED_PIN = 18
IO.setmode(IO.BCM)
IO.setup(PIR_PIN, IO.IN)
IO.setup(MTR_PWR_PIN, IO.OUT, initial=IO.LOW)
IO.setup(MTR_CTL_PIN, IO.OUT, initial=IO.LOW)
IO.setup(LED_PIN, IO.OUT, initial=IO.LOW)

# setup Image draw stuff
stream = io.BytesIO()
font = ImageFont.truetype("fonts/whitrabt.ttf",132)

def led_control(state=None):
    if state==None:
        return
    elif state==0:
        IO.output(LED_PIN, IO.LOW)
    elif state==1:
        IO.output(LED_PIN, IO.HIGH)
        
def release_door():
    p = IO.PWM(MTR_CTL_PIN, 50)
    p.start(10)
    IO.output(MTR_PWR_PIN, IO.HIGH)
    sleep(2)
    #p.ChangeDutyCycle(10)
    #sleep(3)
    IO.output(MTR_PWR_PIN, IO.LOW)
    p.stop()
    
# read names
names = []
with open('names.txt','r') as f:
    for line in f:
        names.append(line.strip('\n'))

while True:
    print "waiting..."
    while not IO.input(PIR_PIN):
        pass
    print "triggered."
    trigger_time = datetime.now()
    
    print "closing door..."
    release_door()
    
    print "turning on lights..."
    led_control(1)
    
    print "capturing image..."
    with picamera.PiCamera(sensor_mode=2) as camera:
        camera.resolution = (2592, 1944)
        camera.start_preview()
        sleep(2)
        camera.capture(stream, quality=95, format='jpeg')
    stream.seek(0)
    image = Image.open(stream)
    
    print "turning off lights..."
    led_control(0)
    
    print "manipulating image..."
    draw = ImageDraw.Draw(image)
    (iw,ih) = image.size
    (fw,fh) = font.getsize("O")
    color1 = (50,120,50)
    color2 = (100,230,100)
    draw.text((10,ih-fh-10),'CAPTURED: ', font=font, fill=color1)
    (fw,fh) = font.getsize('CAPTURED: ')
    draw.text((10+fw,ih-fh-10),trigger_time.strftime('%b %d, %Y  %H:%M:%S'), font=font, fill=color2)
    draw.text((10,ih-(2*fh)-20),'NAME: ', font=font, fill=color1)
    (fw,fh) = font.getsize('NAME: ')
    draw.text((10+fw,ih-(2*fh)-20), random.choice(names), font=font, fill=color2)

    print "saving image..."
    base_name = "img"+trigger_time.strftime('_%Y%m%d_%H%M%S')
    image.save(base_name+".jpg", quality=95)
    image.resize((800,600)).save(base_name+"_small.jpg", filter=Image.ANTIALIAS, quality=95)
    
    print "done."
    break
    sleep(15)
