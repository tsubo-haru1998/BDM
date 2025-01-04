import pigpio
import time
import threading

SERVO_PIN = 12

pi = pigpio.pi()

def set_angle(angle):
    # sleep_timeの間だけ角度をangleに設定
    assert 0 <= angle <= 180, 'angle must be 0 to 180'

    pulse_width = (angle / 180) * (2500 - 500) + 500
    pi.set_servo_pulsewidth(SERVO_PIN, pulse_width)

def play_maracas(bpm, start_angle, end_angle):
    delay = 0.0 # サーボモータを動かすことによる遅延[s]
    period = 60.0 / bpm
    if period / 2 - delay > 0:
        set_angle(end_angle)
        time.sleep(period / 2 - delay)
        set_angle(start_angle)
        time.sleep(period / 2 - delay)
    else:
        set_angle(end_angle)
        set_angle(start_angle)



class MaracasController:
    def __init__(self):
        self.bpm = None
        self.beats_time = None
        self.running = False

    def update_bpm(self, bpm, beats_time):
        with self.lock:
            self.bpm = bpm
            self.beats_time = beats_time

    def start(self):
        if not self.running:
            delay = 0.0 # 拍とマラカスを振るタイミングのずれ
            self.running = True
            time.sleep(self.beats_time[0] + delay)
            threading.Thread(target=self.run).start()

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            with self.lock:
                bpm = self.bpm
                if self.bpm and self.beats_time:
                    play_maracas(bpm, 90, 120)