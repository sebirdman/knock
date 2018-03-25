#!/usr/bin/env python3

from pydub import AudioSegment
from flask import Flask
from multiprocessing import Process, RawValue, Lock
from threading import Thread

import sys
import struct
import time
import getopt
import alsaaudio
import RPi.GPIO as GPIO
import atexit
import wave
import math

app = Flask(__name__)
# playArgs = None

class SoundArgs(object):
   def __init__(self):
       self.is_playing = False
       self.pushed = False
       self.fake = False

   def door_pushed(self):
       self.pushed = True

   def door_unpushed(self):
       self.pushed = False;

   def play(self):
       self.is_playing = True

   def stop(self):
       self.is_playing = False

   def thisistestStart(self):
       self.fake = True

   def thisistestStop(self):
       self.fake = False


@app.route("/")
def hello():
    return "DoorProject"

@app.route("/toggle/<what>")
def toggle(what):

    if what == "sound":
       if playArgs.is_playing:
           playArgs.stop()
       else:
           playArgs.play()
       return "Toggled sound {}".format(playArgs.is_playing)

    if what == "fake":
       if playArgs.fake:
           playArgs.thisistestStop()
           return "Stopped fake door"
       else:
           playArgs.thisistestStart()
           return "Started fake door"

    return "unhandled toggle"


def server(args):
    app.run(host='0.0.0.0', port=80)

def audio(args):
    device = 'default'
    periodSize = 160
    rate = 44100
    channel = 1
    format = alsaaudio.PCM_FORMAT_S16_LE

    f = open("test.raw", 'wb')

    mix = alsaaudio.Mixer(control='Master', id=0, cardindex=-1, device=device)

    mix.setvolume(100, alsaaudio.PCM_PLAYBACK)
    mix.setvolume(100, alsaaudio.PCM_CAPTURE)

    # Open the device in playback mode.
    # out = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, alsaaudio.PCM_NONBLOCK, device=device)
    inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK, device=device)
    inp.setformat(format)
    inp.setchannels(channel)
    inp.setrate(rate)
    inp.setperiodsize(periodSize)

    GPIO.setmode(GPIO.BCM)

    should_listen_door = True
    alarmFile = wave.open('./alarm.wav', 'rb')

    device = 'default'
    device = alsaaudio.PCM(device=device)

    # Set attributes
    device.setchannels(alarmFile.getnchannels())
    device.setrate(alarmFile.getframerate())

    # 8bit is unsigned in wav files
    if alarmFile.getsampwidth() == 1:
        device.setformat(alsaaudio.PCM_FORMAT_U8)
    # Otherwise we assume signed data, little endian
    elif alarmFile.getsampwidth() == 2:
        device.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    elif alarmFile.getsampwidth() == 3:
        device.setformat(alsaaudio.PCM_FORMAT_S24_3LE)
    elif alarmFile.getsampwidth() == 4:
        device.setformat(alsaaudio.PCM_FORMAT_S32_LE)
    else:
        raise ValueError('Unsupported format')

    periodsize = alarmFile.getframerate() / 8

    device.setperiodsize(periodsize)

    alarmData = alarmFile.readframes(periodsize)
    while True:
        l, data = inp.read()

        if l:
            try:
                sound = AudioSegment(data, sample_width=4, channels=1, frame_rate=44100)
                if sound.dBFS > -8:
                    device.write(alarmData)
                    alarmData = alarmFile.readframes(periodsize)
                    print("Door was pressed with {}".format(sound.dBFS))
                    if not data:
                        alarmFile.rewind()
                        data = alarmFile.readframes(periodsize)
                if args.fake:
                    device.write(alarmData)
                    alarmData = alarmFile.readframes(periodsize)
                    if not alarmData:
                        alarmFile.rewind()
                        data = alarmFile.readframes(periodsize)
            except:
                print("Something crashed in the loop")
            f.write(data)
             
#def start_listen():
    # listen = 26
#    GPIO.setup(26, GPIO.OUT)
#    GPIO.output(26, GPIO.LOW)

#def stop_listen():
#    GPIO.output(listen, gpio.HIGH)

#def start_door():
#    # gpio = 16
#    GPIO.setup(16, GPIO.OUT)
#    GPIO.output(16, GPIO.LOW)

#def stop_door():
#    GPIO.output(16, GPIO.HIGH)

#def play_alarm():
    # AudioSegment(data, sample_width=4, channels=1, frame_rate=44100)
#    print("play alarm")

@atexit.register
def goodbye():
#    stop_door()
#    stop_listen()
#    t1.stop()
    GPIO.cleanup()
    print('Done!')


if __name__ == '__main__':
    playArgs = SoundArgs()

    thread1 = Thread( target=server, args=(playArgs, ) )
    thread2 = Thread( target=audio, args=(playArgs, ) )

    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()
