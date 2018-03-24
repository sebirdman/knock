#!/usr/bin/env python

from __future__ import print_function

from pydub import AudioSegment
import sys
import struct
import time
import getopt
import alsaaudio
import RPi.GPIO as GPIO
import atexit
import math

if __name__ == '__main__':

    device = 'default'
    periodSize = 160
    rate = 44100
    channel = 1
    format = alsaaudio.PCM_FORMAT_S16_LE

    opts, args = getopt.getopt(sys.argv[1:], 'd:')
    for o, a in opts:
        if o == '-d':
            device = a

    f = open(args[0], 'wb')

    mix = alsaaudio.Mixer(control='Master', id=0, cardindex=-1, device=device)

    mix.setvolume(100, alsaaudio.PCM_PLAYBACK)
    mix.setvolume(100, alsaaudio.PCM_CAPTURE)

    # Open the device in playback mode.
    out = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, alsaaudio.PCM_NONBLOCK, device=device)
    inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK, device=device)

    out.setformat(format)
    inp.setformat(format)

    out.setchannels(channel)
    inp.setchannels(channel)

    out.setrate(rate)
    inp.setrate(rate)

    inp.setperiodsize(periodSize)
    out.setperiodsize(periodSize)

    GPIO.setmode(GPIO.BCM)



def listen_for_door():
    should_listen_door = True
    while should_listen_door:
        l, data = inp.read()

        if l:
            sound = AudioSegment(data, sample_width=4, channels=1, frame_rate=44100)
            if sound.dBFS > -8:
                print("Door was pressed with {}".format(sound.dBFS))
            # out.write(sound.raw_data)
            f.write(data)

def start_listen():
    # listen = 26
    GPIO.setup(26, GPIO.OUT)
    GPIO.output(26, GPIO.LOW)

def stop_listen():
    GPIO.output(listen, gpio.HIGH)

def start_door():
    # gpio = 16
    GPIO.setup(16, GPIO.OUT)
    GPIO.output(16, GPIO.LOW)

def stop_door():
    GPIO.output(16, GPIO.HIGH)

def play_alarm():
    # AudioSegment(data, sample_width=4, channels=1, frame_rate=44100)
    print("play alarm")

@atexit.register
def goodbye():
    stop_door()
    stop_listen()
    GPIO.cleanup()
    print('Done!')

