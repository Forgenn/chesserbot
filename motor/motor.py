import RPi.GPIO as GPIO
from time import sleep

STEP_ANGLE = 0.087890625

STEP_SLEEP = 0.002
SEQ = [[1,0,0,1],
       [1,0,0,0],
       [1,1,0,0],
       [0,1,0,0],
       [0,1,1,0],
       [0,0,1,0],
       [0,0,1,1],
       [0,0,0,1]]

class Motor:
    def __init__(self, in1, in2, in3, in4):
        self.pins = [in1, in2, in3, in4]
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(in1, GPIO.OUT)
        GPIO.setup(in2, GPIO.OUT)
        GPIO.setup(in3, GPIO.OUT)
        GPIO.setup(in4, GPIO.OUT)

        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.LOW)
        GPIO.output(in3, GPIO.LOW)
        GPIO.output(in4, GPIO.LOW)

        self.angle = 0

    def rotate(self, angle):
        steps = abs(angle // STEP_ANGLE)
        clock = angle < 0

        print(f"Steps: {steps}")

        seq_count = -1 if clock else 0
        for i in range(int(steps)):
            for j, pin in enumerate(self.pins):
                GPIO.output(pin, SEQ[seq_count][j])
                print(SEQ[seq_count][j], end="")

            if clock:
                seq_count = (seq_count - 1) % len(SEQ)
            else:
                seq_count = (seq_count + 1) % len(SEQ)

            sleep(STEP_SLEEP)
