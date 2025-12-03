import smbus
import time

bus = smbus.SMBus(1)
address = 0x42  # UPS HAT I2C address

def read_raw_data():
    try:
        data = bus.read_i2c_block_data(address, 0x00, 8)
        return data
    except Exception as e:
        print("I2C read error:", e)
        return None

def get_voltage(data):
    # інтерпретуємо перші два байти як напругу (мВ)
    voltage_raw = (data[0] << 8) | data[1]
    voltage = voltage_raw / 1000.0  # переводимо у вольти
    return voltage

print("UPS HAT 18306 Monitor\n")

for i in range(5):
    raw = read_raw_data()
    if raw:
        voltage = get_voltage(raw)
        print(f"Read #{i+1}: {raw}")
        print(f"Voltage: {voltage:.2f} V")
    else:
        print("No data.")
    time.sleep(1)

print("Done.")
