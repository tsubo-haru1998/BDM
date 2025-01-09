import pigpio
import time
import threading
import numpy as np

def set_angle(pi, servo_pin, angle):
    # sleep_timeの間だけ角度をangleに設定
    assert 0 <= angle <= 180, 'angle must be 0 to 180'

    max_width = 2500
    min_width = 500

    pulse_width = (angle / 180) * (max_width - min_width) + min_width
    pi.set_servo_pulsewidth(servo_pin, pulse_width)

def play_maracas(bpm, start_angle, end_angle, servo_pin, pi):
    delay = 0.0 # サーボモータを動かすことによる遅延[s]
    period = 60.0 / bpm
    if period / 2 - delay > 0:
        set_angle(pi, servo_pin, end_angle)
        time.sleep(period / 2 - delay)
        set_angle(pi, servo_pin, start_angle)
        time.sleep(period / 2 - delay)
    else:
        set_angle(pi, servo_pin, end_angle)
        set_angle(pi, servo_pin, start_angle)



class GPIOMaracasController:
    def __init__(self, pi):
        self.bpm = None
        self.beats_delay = None
        self.rms = None
        self.running = False
        self.lock = threading.Lock()
        self.run_thread = None
        self.start_angle = 90
        self.servo_pin = 12 # マラカスのピン番号
        self.pi = pi
        set_angle(self.pi, self.servo_pin, self.start_angle)

    def update_bpm(self, bpm, beats_delay, rms):
        with self.lock:
            self.bpm = bpm
            self.rms = rms
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
        set_angle(self.pi, self.servo_pin, self.start_angle)

    def run(self):
        while self.running:
            bpm = self.bpm
            rms = self.rms
            if rms > 0.05:
                rms = 0.05
            end_angle = self.start_angle + 20 + 40 * np.log1p(rms * 20)/np.log(2)
            if bpm:
                play_maracas(bpm, self.start_angle, end_angle, self.servo_pin, self.pi)
            time.sleep(0.001)