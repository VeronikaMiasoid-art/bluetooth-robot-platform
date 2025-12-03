IN1, IN2 = 17, 27  
IN3, IN4 = 22, 23   

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup([IN1, IN2, IN3, IN4], GPIO.OUT, initial=GPIO.LOW)

#  БАЗОВІ ДІЇ 
def stop():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)

# Вперед: ЛІВЕ інвертоване, ПРАВЕ звичайне
def forward():
    GPIO.output(IN1, GPIO.LOW)   
    GPIO.output(IN2, GPIO.HIGH) 
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

# Назад: ЛІВЕ інвертоване, ПРАВЕ звичайне
def backward():
    GPIO.output(IN1, GPIO.HIGH)  
    GPIO.output(IN2, GPIO.LOW)   
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)

# Повороти (короткі імпульси зупинки другого колеса)
def turn_left():
    # Ліве назад (інверсія), праве вперед
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

def turn_right():
    # Ліве вперед (інверсія), праве назад
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)

#  CLI-тест 
if __name__ == "__main__":
    try:
        print("w – вперед | s – назад | a – вліво | d – вправо | x – стоп | q – вихід")
        while True:
            cmd = input("> ").strip().lower()
            if cmd == 'w':
                forward()
            elif cmd == 's':
                backward()
            elif cmd == 'a':
                turn_left()
            elif cmd == 'd':
                turn_right()
            elif cmd == 'x':
                stop()
            elif cmd == 'q':
                stop()
                break
    finally:
        stop()
        GPIO.cleanup()
