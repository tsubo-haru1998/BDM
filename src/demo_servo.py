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
        self.paramlock = threading.Lock()
        self.runninglock = threading.Lock()
        self.run_thread1 = None
        self.run_thread2 = None
        self.start_angle1 = 30
        self.start_angle2 = 110
        self.servo_pin1 = 12 # マラカスのピン番号
        self.servo_pin2 = 23 # マラカス2のピン番号
        self.pi = pi
        set_angle(self.pi, self.servo_pin1, self.start_angle1)
        set_angle(self.pi, self.servo_pin2, self.start_angle2)

    def update_bpm(self, bpm, beats_delay, rms):
        with self.paramlock:
            self.bpm = bpm
            self.rms = rms
        self.beats_delay = beats_delay

    def start(self):
        if not self.running:
            delay = 0.0 # 拍とマラカスを振るタイミングのずれ
            time.sleep(self.beats_delay + delay) # マラカスの始動タイミングの調整
            with self.runninglock:
                self.running = True
            self.run_thread1 = threading.Thread(target=self.run_maracas_1)
            self.run_thread2 = threading.Thread(target=self.run_maracas_2)
            self.run_thread1.start()
            self.run_thread2.start()

    def stop(self):
        with self.runninglock:
            self.running = True
        self.running = False
        if self.run_thread1 and self.run_thread1.is_alive():
            self.run_thread1.join()
            self.run_thread1 = None
        if self.run_thread2 and self.run_thread2.is_alive():
            self.run_thread2.join()
            self.run_thread2 = None
        set_angle(self.pi, self.servo_pin1, self.start_angle1)
        set_angle(self.pi, self.servo_pin2, self.start_angle2)

    def run_maracas_1(self): # right
        while self.running:
            bpm = self.bpm
            rms = self.rms
            if rms > 0.05:
                rms = 0.05
            # end_angle = self.start_angle1 + 20 + 40 * np.log1p(rms * 20)/np.log(2)
            end_angle = self.start_angle1 + 40
            if bpm:
                play_maracas(bpm, self.start_angle1, end_angle, self.servo_pin1, self.pi)

    def run_maracas_2(self): # left
        while self.running:
            bpm = self.bpm
            rms = self.rms
            if rms > 0.05:
                rms = 0.05
            # end_angle = self.start_angle2 + 20 + 40 * np.log1p(rms * 20)/np.log(2)
            end_angle = self.start_angle2 - 40
            if bpm:
                play_maracas(bpm, self.start_angle2, end_angle, self.servo_pin2, self.pi)
