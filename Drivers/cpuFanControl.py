import RPi.GPIO as GPIO
import os
import time
from datetime import datetime

# Log file folder path
logPath = "/home/pi/logs"

# Temperatures
# In case of loud fan noise on low spin speed replace "highTemp = 60" by "highTemp = mediumTemp" to run it always on max spin speed
mediumTemp = 40  # for medium fan spin speed, default = 40*C | 104*F | 313.15K
highTemp = 55  # for high fan spin speed, default = 60*C | 140*F | 333.15K
emergencyTemp = 85  # if this temperature is reaced an emergnecy Shutdown option is enabaled an emergency shutdown will be triggert

# Spin speeds in percent
lowSpinSpeed = 0  # defualt value: low = 0 (off)
mediumSpinSpeed = 65  # defualt value: 65 (some fans have issues to start spinning with 50% or less)
highSpinSpeed = 100  # defualt value: 100 (maximum)

# Other Settings
unit = "Celsius"  # Possible values: "Celsius", "Fahrenheit" or "Kelvin"
gpioPin = 18  # default GPIO Pin (PWM)
pwmFrequency = 50  # PWM frequency in Hz, default = 50Hz
# Do not set to an too low value to prevent from unnecessary File IO operations and CPU performance usage
cycle = 10  # cycle in seconds, recommended = 10 to 30

#Emergency Shutdown
emergencyShutdown = True

# Debug, do not activate for normal usage (high CPU and file IO usage possible)
# True to print current temperatures, expected fan spin speed and used temperature unit
debug = False



GPIO.setmode(GPIO.BCM)
GPIO.setup(gpioPin, GPIO.OUT)  # default Pin 23
pin = GPIO.PWM(gpioPin, pwmFrequency)  # default Pin 23, frequency 50Hz
pin.start(0)

# read temperature from OS generated file
def getCpuTemperature():
  tempFile = open( "/sys/class/thermal/thermal_zone0/temp" )
  cpu_temperatureC = tempFile.read()
  tempFile.close()
  return float(cpu_temperatureC)/1000

# convert degrees Celsius to degrees Fahrenheit
def temperatureCtoF(temperatureC):
  return float((temperatureC * 9.0 / 5.0) + 32.0)

# convert degrees Celsius to Kelvin
def temperatureCtoK(temperatureC):
  return float(temperatureC + 273.15)

# unit check if Celsius, Fahrenheit or Kelvin is in use
def unitCheck(temperature):
  if unit != "Celsius":
    if unit == "Fahrenheit":
      temperature = temperatureCtoF(temperature)
    else:
      temperature = temperatureCtoK(temperature)
  return temperature

# debug prints (do not activate if not needed)
def debugPrintOut(temperature):
  strCpuTempC = "{0:.1f}".format(temperature) + "*C"
  strCpuTempF = "{0:.1f}".format(temperatureCtoF(temperature)) + "*F"
  strCpuTempK = "{0:.1f}".format(temperatureCtoK(temperature)) + " K"
  print(strCpuTempC + " | " + strCpuTempF + " | " + strCpuTempK)

  temperature = unitCheck(temperature)

  if temperature < mediumTemp:
      print("{0:.1f}".format(temperature) + " " + unit + " = low temperature")
      print("expected spin speed: " + str(lowSpinSpeed) + "%\n")
  elif (temperature >= mediumTemp and temperature < highTemp):
      print("{0:.1f}".format(temperature) + " " + unit + " = medium temperature")
      print("expected spin speed: " + str(mediumSpinSpeed) + "%\n")
  else:
      print("{0:.1f}".format(temperature) + " " + unit + " = high temperature")
      print("expected spin speed: " + str(highSpinSpeed) + "%\n")


# main
try:
  if unit != "Celsius" and unit != "Fahrenheit" and unit != "Kelvin":
    print("\n" + "\033[1;31;40m" + "Error: No valid temperature unit choosen.\nFall back to degrees Celsius.\n" + "\033[0m")
    unit = "Celsius"

  while 1:
    temperature = getCpuTemperature()

    if debug:
      debugPrintOut(temperature)

    temperature = unitCheck(temperature)

    if temperature < mediumTemp:
      pin.ChangeDutyCycle(lowSpinSpeed)
    elif (temperature >= mediumTemp and temperature < highTemp):
      pin.ChangeDutyCycle(mediumSpinSpeed)
    else:
      pin.ChangeDutyCycle(highSpinSpeed)

    if(emergencyShutdown and emergencyTemp < temperature):
      date = datetime.now().strftime("%Y-%m-%d | %H:%M:%S")
      logFile = open(logPath + "/emergencyShutdown", "w")
      logFile.write("Emergency Shutdown!\nTemerature reached: " + str(temperature) + "\nTime: " + date + "\n")
      logFile.close()
      os.system("sudo shutdown -h now")

    time.sleep(cycle)
# if manually started can be interrupted clean
except KeyboardInterrupt:
  pass
  pin.stop()
  GPIO.cleanup()
