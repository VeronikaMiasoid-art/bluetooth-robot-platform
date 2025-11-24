from bluezero import peripheral
import RPi.GPIO as GPIO

# ===== Налаштування моторів =====
IN1, IN2, IN3, IN4 = 17, 27, 22, 23
GPIO.setmode(GPIO.BCM)
GPIO.setup([IN1, IN2, IN3, IN4], GPIO.OUT, initial=GPIO.LOW)

def stop():
    for pin in [IN1, IN2, IN3, IN4]:
        GPIO.output(pin, GPIO.LOW)

def forward():
    GPIO.output(IN1, 0); GPIO.output(IN2, 1)
    GPIO.output(IN3, 1); GPIO.output(IN4, 0)

def backward():
    GPIO.output(IN1, 1); GPIO.output(IN2, 0)
    GPIO.output(IN3, 0); GPIO.output(IN4, 1)

def left():
    GPIO.output(IN1, 1); GPIO.output(IN2, 0)
    GPIO.output(IN3, 1); GPIO.output(IN4, 0)

def right():
    GPIO.output(IN1, 0); GPIO.output(IN2, 1)
    GPIO.output(IN3, 0); GPIO.output(IN4, 1)

# ===== Функція на прийом BLE-команди =====
def on_command(value):
    cmd = value.decode('utf-8').strip().upper()
    print("BLE cmd:", cmd)
    if cmd == 'W': forward()
    elif cmd == 'S': backward()
    elif cmd == 'A': left()
    elif cmd == 'D': right()
    else: stop()

# ===== Створення BLE-сервісу =====
UART_SERVICE = '12345678-1234-5678-1234-56789abcdef0'
UART_CHAR = '12345678-1234-5678-1234-56789abcdef1'

rx_char = peripheral.Characteristic(UART_CHAR,
                                    ['write'],
                                    write_callback=on_command)

srv = peripheral.Service(UART_SERVICE, True)
srv.add_characteristic(rx_char)

ble = peripheral.Peripheral(adapter_addr=None, local_name='PiCar')
ble.add_service(srv)

try:
    print("🔵 BLE active — шукай 'PiCar' у LightBlue/nRF Connect")
    ble.publish()
except KeyboardInterrupt:
    stop()
    GPIO.cleanup()
    print("Зупинено.")
