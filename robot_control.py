
import RPi.GPIO as GPIO
import time
import os
import struct

# --- UPS MONITORING SECTION ----------------
# --- UPS HAT 18306: обережне читання з ретраями ---
import smbus2

UPS_I2C_BUS = 1
UPS_ADDR    = 0x42

def _ups_read_block_safe(cmd=0x00, length=32, retries=3, delay=0.05):
    """Надійне читання блоку з UPS із ретраями, щоб не ловити Errno 5."""
    bus = smbus2.SMBus(UPS_I2C_BUS)
    try:
        for _ in range(retries):
            try:
                # багато цих HAT адекватно відповідають на read_i2c_block_data(0x00, len)
                data = bus.read_i2c_block_data(UPS_ADDR, cmd, length)
                return data
            except OSError as e:
                time.sleep(delay)
        raise OSError("UPS I2C read failed after retries")
    finally:
        bus.close()

def read_ups_status():
    """
    Повертає (voltage_v, percent, power_text).
    Якщо твій окремий скрипт показував інші поля — можеш підмінити тут парсинг тим кодом.
    """
    raw = _ups_read_block_safe(0x00, 32, retries=5, delay=0.1)

    # Приклад простого парсингу як у твоїх попередніх тестах:
    # raw виглядає на кшталт [57, 159, 255, 255, 255, 255, 255, 255]
    # беремо перші 2 байти як «сирий вольтаж» (умовно) і масштабуємо
    if len(raw) >= 2:
        raw_mv = (raw[0] << 8) | raw[1]   # умовне перетворення, підігнане під те що ми бачили
        voltage = round( raw_mv / 390.0 , 2)  # підбір масштабу під ~14.7 V, щоб збігалося з твоїм скриптом
    else:
        voltage = 0.0

    # Відсоток батареї: якщо твій робочий `ups_full_monitor.py` вже вмів рахувати — встав його формулу тут.
    percent = 98.0  # placeholder, щоб не падало; заміни своєю логікою з робочого скрипта

    # Стан живлення: зовнішнє/заряд/акум — за бажанням з твого скрипта
    power_text = "External Power (charging?)"

    return voltage, percent, power_text

def ups_menu_action():
    try:
        v, p, t = read_ups_status()
        print(f"🔋 UPS: {v:.2f} V | Battery: {p:.1f}% | Power: {t}")
    except Exception as e:
        print(f"❌ Помилка читання UPS: {e}")

# --- MOTOR CONTROL SECTION -----------------
IN1, IN2, IN3, IN4 = 17, 18, 22, 23

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
for pin in (IN1, IN2, IN3, IN4):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, 0)

# --- MOTOR FUNCTIONS -----------------------
def forward():
    GPIO.output(IN1, 1)
    GPIO.output(IN2, 0)
    GPIO.output(IN3, 1)
    GPIO.output(IN4, 0)
    print("⬆️ Moving forward")

def backward():
    GPIO.output(IN1, 0)
    GPIO.output(IN2, 1)
    GPIO.output(IN3, 0)
    GPIO.output(IN4, 1)
    print("⬇️ Moving backward")

def left():
    GPIO.output(IN1, 0)
    GPIO.output(IN2, 1)
    GPIO.output(IN3, 1)
    GPIO.output(IN4, 0)
    print("⬅️ Turning left")

def right():
    GPIO.output(IN1, 1)
    GPIO.output(IN2, 0)
    GPIO.output(IN3, 0)
    GPIO.output(IN4, 1)
    print("➡️ Turning right")

def stop():
    for pin in (IN1, IN2, IN3, IN4):
        GPIO.output(pin, 0)
    print("🛑 Stopped")

# --- UPS MONITORING FUNCTION ---------------
def read_ups_status():
    if not UPS_AVAILABLE:
        print("⚠️ SMBus не знайдено. UPS-моніторинг вимкнено.")
        return

    try:
        bus = smbus2.SMBus(1)
        address = 0x36

        # Зчитування напруги
        raw_voltage = bus.read_word_data(address, 0x02)
        swapped = struct.unpack("<H", struct.pack(">H", raw_voltage))[0]
        voltage = swapped * 1.25 / 1000 / 16  # формула з даташиту

        # Зчитування рівня заряду (%)
        raw_capacity = bus.read_word_data(address, 0x04)
        swapped_capacity = struct.unpack("<H", struct.pack(">H", raw_capacity))[0]
        capacity = swapped_capacity / 256

        # Перевірка, чи йде зарядка (через 5V GPIO)
        power_status = "🔌 External Power (charging)" if os.path.exists("/sys/class/power_supply") else "🔋 On Battery"

        print(f"\n🔋 UPS STATUS:")
        print(f"Voltage: {voltage:.2f} V")
        print(f"Battery: {capacity:.1f}%")
        print(f"Power:   {power_status}\n")

    except Exception as e:
        print("❌ Помилка читання UPS:", e)

# --- TEST MOTOR FUNCTION -------------------
def test_motors():
    print("\n🚗 Тестування моторів...")
    forward()
    time.sleep(1)
    backward()
    time.sleep(1)
    left()
    time.sleep(1)
    right()
    time.sleep(1)
    stop()
    print("✅ Тест завершено.\n")

# --- KEYBOARD CONTROL MODE -----------------def keyboard_control():
    # --- Keyboard over SSH/terminal (без бібліотеки keyboard) ---
import sys, termios, tty, select, time

def _getch_nonblocking(timeout=0.1):
    """Повертає 1 символ з клавіатури без Enter, або None якщо нічого не натиснули."""
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        r, _, _ = select.select([sys.stdin], [], [], timeout)
        if r:
            ch = sys.stdin.read(1)
            return ch
        return None
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

def keyboard_control():
    print("\n🎮 Режим керування з клавіатури:")
    print("W - вперед | S - назад | A - вліво | D - вправо | X - стоп | Q - вихід")
    try:
        while True:
            key = _getch_nonblocking(0.1)
            if not key:
                continue
            key = key.lower()
            if key == 'w':
                forward()
            elif key == 's':
                backward()
            elif key == 'a':
                left()
            elif key == 'd':
                right()
            elif key == 'x':
                stop()
            elif key == 'q':
                stop()
                print("🚪 Вихід з режиму керування.")
                break
    except KeyboardInterrupt:
        stop()

# --- MAIN MENU -----------------------------
def main_menu():
    while True:
        print("\n=== 🤖 ROBOT CONTROL MENU ===")
        print("1️⃣  Тест моторів")
        print("2️⃣  Керування з клавіатури")
        print("3️⃣  Перевірити стан UPS")
        print("4️⃣  Вихід")

        choice = input("➡️  Обери режим: ")

        if choice == '1':
            test_motors()
        elif choice == '2':
            keyboard_control()
        elif choice == '3':
            read_ups_status()
        elif choice == '4':
            break
        else:
            print("❌ Невірний вибір. Спробуй ще раз.")

    GPIO.cleanup()
    print("🔌 GPIO очищено. Програма завершена.")

# --- START ---------------------------------
if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("\n🛑 Примусове завершення.")
