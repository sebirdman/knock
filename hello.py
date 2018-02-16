from flask import Flask
import RPi.GPIO as GPIO
import atexit
import alsaaudio

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/toggle/<what>")
def readPin(what):

   channel = None

   if what == "door":
      channel = 16
   if what == "listen":
      channel = 26
      listen = 0 if listen == 1 else 1

   if channel is None:
      return "nothing"

   current = GPIO.input(channel)

   return "gpio {} - {}".format(channel, current)

if __name__ == "__main__":

    device = 'default'
    periodSize = 160
    rate = 44100
    channel = 1
    listen = 0

    f = open("out.raw", 'wb')

    mix = alsaaudio.Mixer(control='Master', id=0, cardindex=-1, device=device)

    mix.setvolume(100, alsaaudio.PCM_PLAYBACK)
    mix.setvolume(100, alsaaudio.PCM_CAPTURE)

    # Open the device in playback mode.
    out = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, alsaaudio.PCM_NONBLOCK, device=device)
    inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK, device=device)

    out.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    inp.setformat(alsaaudio.PCM_FORMAT_S32_LE)

    out.setchannels(channel)
    inp.setchannels(channel)

    out.setrate(rate)
    inp.setrate(rate)

    out.setperiodsize(periodSize)
    inp.setperiodsize(periodSize)

    GPIO.setmode(GPIO.BCM)

    GPIO.setup([16, 26], GPIO.OUT, initial=GPIO.HIGH)

    app.run(host='0.0.0.0', port=80, debug=True)

    while True:
        if listen == 1:
            print("hello")



@atexit.register
def goodbye():
    GPIO.cleanup()
    print('Done!')
