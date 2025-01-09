from process_music import rec_from_stream, get_bpm, get_volume
from demo_servo import GPIOMaracasController
from pwm_servo import PWMController
import librosa
import numpy as np
import pigpio
import sys
import sounddevice as sd
from collections import deque
import time

def initialize_JIT_conpile():
    # ランダムノイズ信号を生成
    sr = 22050  # サンプリングレート
    duration = 1  # 秒
    random_signal = np.random.rand(sr * duration)

    # JITコンパイルを初期化
    _, _ = librosa.beat.beat_track(y=random_signal, sr=sr)


def test(get_ready_LED_pin):
    dev_index = 2 # マイクのデバイス番号。調べる必要あり
    max_store_time = 20 # BPM計算に用いる音の最大長[s]
    update_interval = 2 # BPM計算を行う間隔[s]
    threshold = 2**-8 # 楽器を鳴らし始める音量
    REC_BUTTON_PIN = 18 # 録音開始/停止の切り替えボタン

    pi = pigpio.pi()
    maracas_controller = GPIOMaracasController(pi)

    initialize_JIT_conpile()

    sd.default.device = [dev_index, None] # Input, Outputデバイス指定
    input_device_info = sd.query_devices(device=sd.default.device[0])
    sr_in = int(input_device_info["default_samplerate"]) # Input Device(Mic.)のサンプリングレート

    audio_buffer = deque(maxlen=max_store_time * sr_in) # リングバッファ

    stream = rec_from_stream(audio_buffer, sr_in)

    def play_toggle_program(gpio, level, tick):
        # ボタンが押された時に演奏を開始/停止する

        if stream.active:
            # 演奏中止
            maracas_controller.stop()
            time.sleep(0.5)
            stream.stop()
            audio_buffer.clear()
            print("stream stopped")

        else:
            # 演奏開始
            stream.start()
            print("stream started")

    # ボタンのGPIO設定
    pi.set_mode(REC_BUTTON_PIN, pigpio.INPUT)
    pi.set_pull_up_down(REC_BUTTON_PIN, pigpio.PUD_UP)
    pi.set_glitch_filter(REC_BUTTON_PIN, 30000) # ノイズにより複数回コールバックが呼ばれるのを防ぐ対策で30msのデバウンズを設ける

    # 準備完了のLED点灯
    pi.set_mode(get_ready_LED_pin, pigpio.OUTPUT)
    pi.write(get_ready_LED_pin, True)

    # ボタンのコールバック設定
    pi.callback(REC_BUTTON_PIN, pigpio.FALLING_EDGE, play_toggle_program)

    print("start!")
    while True:
        if stream.active:
            time.sleep(update_interval)
            frames = np.array(audio_buffer)
            rms = get_volume(frames)
            if (rms > threshold):
                bpm, beats_delay = get_bpm(frames, sr_in)
                print("BPM:", bpm)
                maracas_controller.update_bpm(bpm, beats_delay, rms)
                maracas_controller.start()
            else:
                maracas_controller.stop()
        else:
            time.sleep(0.1)



if __name__ == "__main__":
    args = sys.argv
    if len(args) == 2:
        try:
            test(int(args[1]))
        except ValueError:
            print("ピン番号は整数である必要があります")
