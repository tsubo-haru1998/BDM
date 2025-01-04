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

def shake_maracas_thread(bpm, start_angle, end_angle):
    delay = 0.0 # サーボモータを動かすことによる遅延[s]
    period = 60.0 / bpm
    set_angle(end_angle)
    time.sleep(period / 2 - delay)
    set_angle(start_angle)
    time.sleep(period / 2 - delay)


def play_maracas(bpm, beats_time):
    prev_time = time.time()
    for beat_time in beats_time:
        cur_time = time.time()
        time_to_wait = beat_time - (cur_time - prev_time)
        if time_to_wait > 0:
            time.sleep(time_to_wait)

        # 非同期で振る動作を開始
        threading.Thread(target=shake_maracas_thread, args=(bpm, 90, 120)).start()


class MaracasController:
    def __init__(self):
        self.bpm = None
        self.beats_time_time = None
        self.running = False
        self.lock = threading.Lock()

    def update_bpm(self, bpm, beats_time):
        with self.lock:
            self.bpm = bpm
            self.beats_time = beats_time

    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.run).start()

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            with self.lock:
                bpm = self.bpm
                beats_time = self.beats_time
                if self.bpm and self.beats_time:
                    play_maracas(bpm, beats_time)