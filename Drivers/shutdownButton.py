import RPi.GPIO as GPIO
import time
import os

GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(24, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

def Shutdown(channel):
  os.system("sudo shutdown -h now")
def Restart(channel):
  os.system("sudo shutdown -r now")

GPIO.add_event_detect(23, GPIO.FALLING, callback = Restart, bouncetime = 2000)
GPIO.add_event_detect(24, GPIO.FALLING, callback = Shutdown, bouncetime = 2000)

while True:
  time.sleep(1)
