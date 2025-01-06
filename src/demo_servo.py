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
        self.beats_delay = None
        self.running = False
        self.lock = threading.Lock()
        self.run_thread = None
        self.start_angle = 90
        self.end_angle = 120
        set_angle(self.start_angle)

    def update_bpm(self, bpm, beats_delay):
        with self.lock:
            self.bpm = bpm
            self.beats_delay = beats_delay

    def start(self):
        delay = 0.0 # 拍とマラカスを振るタイミングのずれ
        time.sleep(self.beats_delay + delay) # マラカスの始動タイミングの調整

        if not self.running:
            self.running = True
            self.run_thread = threading.Thread(target=self.run)
            self.run_thread.start()

    def stop(self):
        self.running = False
        if self.run_thread and self.run_thread.is_alive():
            self.run_thread.join()
            self.run_thread = None
        set_angle(self.start_angle)

    def run(self):
        while self.running:
            with self.lock:
                bpm = self.bpm
                if bpm:
                    play_maracas(bpm, self.start_angle, self.end_angle)