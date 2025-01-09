import Adafruit_PCA9685
import time
import threading
import numpy as np

def set_angle(pwm, servo_channel, angle):
    # sleep_timeの間だけ角度をangleに設定
    assert 0 <= angle <= 180, 'angle must be 0 to 180'

    max_width = 2500
    min_width = 500

    pulse_width = (angle / 180) * (max_width - min_width) + min_width
    pwm.set_pwm(servo_channel, 0, pulse_width)

def play_maracas(bpm, start_angle, end_angle, servo_channel, pwm):
    delay = 0.0 # サーボモータを動かすことによる遅延[s]
    period = 60.0 / bpm
    if period / 2 - delay > 0:
        set_angle(pwm, servo_channel, end_angle)
        time.sleep(period / 2 - delay)
        set_angle(pwm, servo_channel, start_angle)
        time.sleep(period / 2 - delay)
    else:
        set_angle(pwm, servo_channel, end_angle)
        set_angle(pwm, servo_channel, start_angle)

class PWMController:
    def __init__(self, pwm):
        self.bpm = None
        self.beats_delay = None
        self.rms = None
        self.running = False
        self.lock = threading.Lock()
        self.run_thread = None
        self.start_angle = 90
        self.maracas_servo_channel = 0 # マラカスのピン番号
        self.pwm = pwm
        set_angle(self.pwm, self.maracas_servo_channel, self.start_angle)

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
        set_angle(self.pwm, self.maracas_servo_channel, self.start_angle)

    def run(self):
        while self.running:
            with self.lock:
                bpm = self.bpm
                rms = self.rms
            if rms > 1:
                rms = 1
            end_angle = self.start_angle + 60 * np.log1p(rms)/np.log(2)
            if bpm:
                play_maracas(bpm, self.start_angle, end_angle, self.maracas_servo_channel, self.pwm)
