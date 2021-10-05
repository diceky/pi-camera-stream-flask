#Modified by diceky
#Date: 05.10.21
#Desc: This web application serves a motion JPEG stream + remote controlled car controls
# main.py

# import the necessary packages
from flask import Flask, render_template, Response, request
from camera import VideoCamera
import time
import threading
import os
import RPi.GPIO as GPIO
from time import sleep
import atexit

# Set RPi GPIO pin numbers
GPIO.setmode(GPIO.BCM)
enA=13
enB=12
in1=22
in2=27
in3=24
in4=23
led=17

# Initialize GPIO
GPIO.setup(enA, GPIO.OUT)
GPIO.setup(enB, GPIO.OUT)
GPIO.setup(in1, GPIO.OUT)
GPIO.setup(in2, GPIO.OUT)
GPIO.setup(in3, GPIO.OUT)
GPIO.setup(in4, GPIO.OUT)
GPIO.setup(led, GPIO.OUT)
pwmA=GPIO.PWM(enA,50)
pwmB=GPIO.PWM(enB,50)

# Turn on LED
GPIO.output(led,True)

pi_camera = VideoCamera(flip=True) # flip pi camera if upside down.

# Cleaning up before exit
def close_running_threads():
    pwmA.stop()
    pwmB.stop()
    GPIO.cleanup()
    print("GPIO cleanup complete, ready to finish")

# App Globals
app = Flask(__name__)
pwmSpeed = 30

@app.route('/', methods=["GET","POST"])
def index():
    global pwmSpeed
    if request.method == 'POST':
        if request.form['submit_button'] == 'Forward':
            #forward
            print("Forward")
            GPIO.output(in1,False)
            GPIO.output(in2,True)
            GPIO.output(in3,False)
            GPIO.output(in4,True)
            sleep(0.1)
            pwmA.start(pwmSpeed)
            pwmB.start(pwmSpeed)
        elif request.form['submit_button'] == 'Back':
            #back
            print("Back")
            GPIO.output(in1,True)
            GPIO.output(in2,False)
            GPIO.output(in3,True)
            GPIO.output(in4,False)
            sleep(0.1)
            pwmA.start(pwmSpeed)
            pwmB.start(pwmSpeed)
        elif request.form['submit_button'] == 'Left':
            #left
            print("Left")
            GPIO.output(in1,True)
            GPIO.output(in2,False)
            GPIO.output(in3,False)
            GPIO.output(in4,True)
            sleep(0.1)
            pwmA.start(50)
            pwmB.start(50)
        elif request.form['submit_button'] == 'Right':
            #right
            print("Right")
            GPIO.output(in1,False)
            GPIO.output(in2,True)
            GPIO.output(in3,True)
            GPIO.output(in4,False)
            sleep(0.1)
            pwmA.start(50)
            pwmB.start(50)
        elif request.form['submit_button'] == 'Stop':
            #stop
            print("Stop")
            GPIO.output(in1,False)
            GPIO.output(in2,False)
            GPIO.output(in3,False)
            GPIO.output(in4,False)
            pwmA.stop()
            pwmB.stop()
        elif request.form['submit_button'] == 'Speed':
            # change PWM cycle
            print(request.form['value'])
            pwmSpeed = int(request.form['value'])
        else:
            pass # unknown
    return render_template('index.html') #you can customze index.html here

def gen(camera):
    #get camera frame
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(pi_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    atexit.register(close_running_threads)
    app.run(host='0.0.0.0', debug=False)
