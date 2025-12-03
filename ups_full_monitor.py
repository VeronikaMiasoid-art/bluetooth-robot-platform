import smbus
import time
from datetime import datetime

bus = smbus.SMBus(1)
ADDR = 0x42  # UPS HAT I2C address

def read_raw():
    try:
        return bus.read_i2c_block_data(ADDR, 0x00, 8)
    except Exception as e:
        print("I2C Error:", e)
        return None

def get_voltage(data):
    voltage_raw = (data[0] << 8) | data[1]
    return voltage_raw / 1000.0

def get_status(data):
    # другий байт часто кодує статуси живлення
    if data[1] > 200:
        return "⚡ Charging (external power)"
    elif data[1] < 150:
        return "Battery mode"
    else:
        return "Unknown"

def get_battery_percent(voltage):
    # 12.0V — майже розряджено, 14.8V — повністю заряджено
    percent = (voltage - 12.0) / (14.8 - 12.0) * 100
    percent = max(0, min(100, percent))
    return percent

print("UPS HAT 18306 — Live Monitor\n")

try:
    while True:
        data = read_raw()
        if not data:
            print("UPS not responding.")
            time.sleep(2)
            continue

        voltage = get_voltage(data)
        percent = get_battery_percent(voltage)
        status = get_status(data)

        now = datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] Voltage: {voltage:.2f} V | Battery: {percent:.1f}% | {status}")
        time.sleep(2)

except KeyboardInterrupt:
    print("Monitoring stopped.")
