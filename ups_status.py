import smbus
import time

# IP5306 I2C address
IP5306_ADDR = 0x75  
bus = smbus.SMBus(1)

def read_register(addr, reg):
    try:
        return bus.read_byte_data(addr, reg)
    except:
        return None

def get_battery_level(addr):
    data = read_register(addr, 0x78)
    if data is None:
        return None
    # У IP5306 нижні 2 біти кодують рівень заряду
    level = data & 0xF0
    if level == 0xE0:
        return 100
    elif level == 0xC0:
        return 75
    elif level == 0x80:
        return 50
    elif level == 0x00:
        return 25
    else:
        return 0

def get_power_status(addr):
    data = read_register(addr, 0x70)
    if data is None:
        return None
    # Біти 5 і 4 вказують на джерело живлення
    if data & 0x10:
        return "⚡ External Power (charging)"
    else:
        return "Battery mode"

# ---- main loop ----
for address in [0x42, 0x75]:
    print(f"Trying UPS at I2C address: 0x{address:02X}")
    level = get_battery_level(address)
    status = get_power_status(address)

    if level is not None:
        print(f"Battery Level: {level}%")
        print(f"Power Status: {status}")
        break
else:
    print("⚠️ No UPS found at 0x42 or 0x75")

print("Done.")
