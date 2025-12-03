import pigpio
import time

class L298NDriver:
    """
    Драйвер для L298N з плавним розгоном/гальмуванням.
    Працює з pigpiod (pigpio daemon).
    """

    def __init__(self,
                 ENA=18, IN1=17, IN2=27,
                 ENB=19, IN3=22, IN4=23,
                 pwm_freq=1000,
                 invert_left=False,
                 invert_right=False):
        self.ENA, self.IN1, self.IN2 = ENA, IN1, IN2
        self.ENB, self.IN3, self.IN4 = ENB, IN3, IN4
        self.pwm_freq = pwm_freq
        self.invert_left = invert_left
        self.invert_right = invert_right

        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("pigpio daemon not running. Run: sudo systemctl start pigpiod")

        for p in [self.IN1, self.IN2, self.IN3, self.IN4, self.ENA, self.ENB]:
            self.pi.set_mode(p, pigpio.OUTPUT)

        self.pi.set_PWM_frequency(self.ENA, self.pwm_freq)
        self.pi.set_PWM_frequency(self.ENB, self.pwm_freq)

        # поточні швидкості (0..255)
        self.left_speed = 0
        self.right_speed = 0
        self.left_dir = 0   # -1 back, 0 stop, 1 fwd
        self.right_dir = 0

        self.stop(hard=True)

    #  низькорівневі сетери 
    def _set_left_dir(self, d):
        if self.invert_left:
            d = -d
        if d == 1:
            self.pi.write(self.IN1, 1); self.pi.write(self.IN2, 0)
        elif d == -1:
            self.pi.write(self.IN1, 0); self.pi.write(self.IN2, 1)
        else:
            self.pi.write(self.IN1, 0); self.pi.write(self.IN2, 0)
        self.left_dir = d

    def _set_right_dir(self, d):
        if self.invert_right:
            d = -d
        if d == 1:
            self.pi.write(self.IN3, 1); self.pi.write(self.IN4, 0)
        elif d == -1:
            self.pi.write(self.IN3, 0); self.pi.write(self.IN4, 1)
        else:
            self.pi.write(self.IN3, 0); self.pi.write(self.IN4, 0)
        self.right_dir = d

    def _set_left_pwm(self, sp):
        sp = max(0, min(255, int(sp)))
        self.pi.set_PWM_dutycycle(self.ENA, sp)
        self.left_speed = sp

    def _set_right_pwm(self, sp):
        sp = max(0, min(255, int(sp)))
        self.pi.set_PWM_dutycycle(self.ENB, sp)
        self.right_speed = sp

    #  базові команди 
    def set_left(self, direction, speed):
        """direction: -1/0/1, speed: 0..255"""
        self._set_left_dir(direction)
        self._set_left_pwm(speed)

    def set_right(self, direction, speed):
        self._set_right_dir(direction)
        self._set_right_pwm(speed)

    def ramp(self, left_dir, right_dir, target_speed,
             ramp_time=0.7, steps=25):
        """
        Плавний розгін/гальмування.
        target_speed: 0..255
        """
        target_speed = max(0, min(255, int(target_speed)))

        # якщо міняємо напрям — спершу загальмуємо до 0
        if left_dir != self.left_dir or right_dir != self.right_dir:
            self._set_left_pwm(0)
            self._set_right_pwm(0)
            time.sleep(0.05)

        self._set_left_dir(left_dir)
        self._set_right_dir(right_dir)

        for s in range(steps + 1):
            sp = int(target_speed * s / steps)
            self._set_left_pwm(sp)
            self._set_right_pwm(sp)
            time.sleep(ramp_time / steps)

    def stop(self, hard=False):
        """hard=True: миттєво; hard=False: плавно"""
        if hard:
            self._set_left_pwm(0)
            self._set_right_pwm(0)
            self._set_left_dir(0)
            self._set_right_dir(0)
        else:
            # плавне гальмування
            cur = max(self.left_speed, self.right_speed)
            for sp in range(cur, -1, -10):
                self._set_left_pwm(sp)
                self._set_right_pwm(sp)
                time.sleep(0.02)
            self._set_left_dir(0)
            self._set_right_dir(0)

    #  рухи для платформи 
    def forward(self, speed=180, ramp_time=0.8):
        self.ramp(1, 1, speed, ramp_time=ramp_time)

    def backward(self, speed=180, ramp_time=0.8):
        self.ramp(-1, -1, speed, ramp_time=ramp_time)

    def turn_left(self, speed=170):
        # диференціальний поворот: ліве повільніше
        self.set_left(1, int(speed * 0.35))
        self.set_right(1, speed)

    def turn_right(self, speed=170):
        self.set_left(1, speed)
        self.set_right(1, int(speed * 0.35))

    def spin_left(self, speed=160):
        # поворот на місці
        self.set_left(-1, speed)
        self.set_right(1, speed)

    def spin_right(self, speed=160):
        self.set_left(1, speed)
        self.set_right(-1, speed)

    def close(self):
        self.stop(hard=True)
        self.pi.stop()
