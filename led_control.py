import RPi.GPIO as GPIO
from enum import Enum

class LedType(Enum):
    Green = 0
    Yellow = 1
    Red = 2

GREEN_LED_PIN: int = 17
YELLOW_LED_PIN: int = 27
RED_LED_PIN: int = 22

class LedControl():
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(GREEN_LED_PIN, GPIO.OUT)
        GPIO.setup(YELLOW_LED_PIN, GPIO.OUT)
        GPIO.setup(RED_LED_PIN, GPIO.OUT)

        GPIO.output(RED_LED_PIN, GPIO.LOW)
        GPIO.output(YELLOW_LED_PIN, GPIO.LOW)
        GPIO.output(GREEN_LED_PIN, GPIO.LOW)

    # LED点灯
    def led_on(self, led_type: LedType):
        emit_type = GPIO.HIGH
        self.led_emit(led_type, emit_type)

    # LED消灯
    def led_off(self, led_type: LedType):
        emit_type = GPIO.LOW
        self.led_emit(led_type, emit_type)

    def led_emit(self, led_type, emit_type):
        if led_type is LedType.Red:
            GPIO.output(YELLOW_LED_PIN, emit_type)
            GPIO.output(RED_LED_PIN, emit_type)
        elif led_type is LedType.Yellow:
            GPIO.output(YELLOW_LED_PIN, emit_type)
        else:
            GPIO.output(GREEN_LED_PIN, emit_type)
