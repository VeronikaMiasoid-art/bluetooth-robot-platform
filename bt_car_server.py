# bt_car_server.py
import time
from motors_pigpio import L298NDriver

# Для SPP потрібен PyBluez:
# sudo apt install -y bluetooth python3-bluez
import bluetooth

driver = L298NDriver(
    ENA=18, IN1=17, IN2=27,
    ENB=19, IN3=22, IN4=23,
)

speed = 180

def handle_command(cmd: str):
    global speed
    cmd = cmd.strip().upper()

    if cmd.startswith("V"):
        try:
            speed = int(cmd[1:])
            speed = max(0, min(255, speed))
            print("Speed set to", speed)
        except:
            print("Bad speed command")
        return

    if cmd == "F":
        driver.forward(speed)
    elif cmd == "B":
        driver.backward(speed)
    elif cmd == "L":
        driver.turn_left(speed)
    elif cmd == "R":
        driver.turn_right(speed)
    elif cmd == "SL":
        driver.spin_left(speed)
    elif cmd == "SR":
        driver.spin_right(speed)
    elif cmd == "S":
        driver.stop(hard=False)
    else:
        print("Unknown cmd:", cmd)

def main():
    print("Starting Bluetooth SPP server...")

    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", bluetooth.PORT_ANY))
    server_sock.listen(1)

    port = server_sock.getsockname()[1]
    uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

    bluetooth.advertise_service(
        server_sock,
        "PiCarSPP",
        service_id=uuid,
        service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
        profiles=[bluetooth.SERIAL_PORT_PROFILE]
    )

    print(f"Waiting for connection on RFCOMM channel {port}...")

    client_sock, client_info = server_sock.accept()
    print("Connected:", client_info)

    try:
        buffer = ""
        while True:
            data = client_sock.recv(64)
            if not data:
                break
            buffer += data.decode("utf-8", errors="ignore")

            # команди можуть бути підряд, розділені \n
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if line.strip():
                    handle_command(line)

    except KeyboardInterrupt:
        pass
    finally:
        print("Closing...")
        driver.close()
        client_sock.close()
        server_sock.close()

if __name__ == "__main__":
    main()
