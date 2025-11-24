import smbus
import time

bus = smbus.SMBus(1)
address = 0x42

print("🔋 Reading UPS HAT data...\n")

for i in range(5):
    try:
        data = bus.read_i2c_block_data(address, 0x00, 8)
        print(f"Read #{i+1}: {data}")

        # (опціонально) перші байти можна інтерпретувати як напругу або струм
        # залежно від моделі UPS HAT (треба буде уточнити схему)
        # Наприклад:
        voltage = (data[0] << 8 | data[1]) / 1000.0
        print(f"Approx. Voltage: {voltage:.2f} V\n")

        time.sleep(1)
    except Exception as e:
        print("Error:", e)
        time.sleep(2)

print("✅ Done reading UPS HAT data.")

