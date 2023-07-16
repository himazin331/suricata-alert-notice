import RPi.GPIO as GPIO

BZ_PIN: int = 18

class BzControl():
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(BZ_PIN, GPIO.OUT)
        GPIO.output(BZ_PIN, GPIO.LOW)

    def bz_beep(self):
        GPIO.output(BZ_PIN, GPIO.HIGH)

    def bz_stop(self):
        GPIO.output(BZ_PIN, GPIO.LOW)
