from process_music import rec, get_bpm, IsMusicPlaying
from demo_servo import MaracasController
import librosa
import numpy as np
import pigpio
import sys

def test(get_ready_LED_pin):
    dev_index = 2 # マイクのデバイス番号。調べる必要あり
    pi = pigpio.pi()

    maracas_controller = MaracasController(pi)

    # ランダムノイズ信号を生成
    sr = 22050  # サンプリングレート
    duration = 1  # 秒
    random_signal = np.random.rand(sr * duration)

    # JITコンパイルを初期化
    _, _ = librosa.beat.beat_track(y=random_signal, sr=sr)

    # 準備完了のLED点灯
    pi.set_mode(get_ready_LED_pin, pigpio.OUTPUT)
    pi.write(get_ready_LED_pin, True)

    print("start!")
    while True:
        frames, samp_rate = rec(dev_index)
        if IsMusicPlaying(frames):
            bpm, beats_delay = get_bpm(frames, samp_rate)
            print("BPM:", bpm)
            maracas_controller.update_bpm(bpm, beats_delay)
            maracas_controller.start(pi)
        else:
            maracas_controller.stop(pi)

if __name__ == "__main__":
    args = sys.argv
    if len(args) == 2:
        try:
            test(int(args[1]))
        except ValueError:
            print("ピン番号は整数である必要があります")
