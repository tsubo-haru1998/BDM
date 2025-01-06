from process_music import rec, get_bpm, IsMusicPlaying
from demo_servo import MaracasController
import librosa
import numpy as np
import pigpio

def test():
    dev_index = 2 # マイクのデバイス番号。調べる必要あり
    get_ready_LED_pin = 17 # 準備完了の合図を出すLEDのピン番号
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
    test()