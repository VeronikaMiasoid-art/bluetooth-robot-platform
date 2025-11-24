import time
from motors_pigpio import L298NDriver

# тут за потреби міняєм піни 
driver = L298NDriver(
    ENA=18, IN1=17, IN2=27,
    ENB=19, IN3=22, IN4=23,
    invert_left=False,
    invert_right=False
)

def test_sequence():
    print("Forward...")
    driver.forward(180); time.sleep(2)

    print("Left turn...")
    driver.turn_left(170); time.sleep(1)

    print("Forward...")
    driver.forward(180); time.sleep(2)

    print("Right turn...")
    driver.turn_right(170); time.sleep(1)

    print("Backward...")
    driver.backward(170); time.sleep(2)

    print("Spin left...")
    driver.spin_left(160); time.sleep(1)

    print("Stop...")
    driver.stop(hard=False); time.sleep(1)

def test_each_motor():
    print("Left motor forward...")
    driver.set_left(1, 180); driver.set_right(0, 0); time.sleep(2)
    driver.stop(hard=False); time.sleep(1)

    print("Right motor forward...")
    driver.set_left(0, 0); driver.set_right(1, 180); time.sleep(2)
    driver.stop(hard=False); time.sleep(1)

if __name__ == "__main__":
    try:
        test_each_motor()
        test_sequence()
    finally:
        driver.close()
