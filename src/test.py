from process_music import rec, get_bpm, IsMusicPlaying
from demo_servo import MaracasController
import librosa
import numpy as np

def test():
    dev_index = 2 # マイクのデバイス番号。調べる必要あり

    maracas_controller = MaracasController()

    # ランダムノイズ信号を生成
    sr = 22050  # サンプリングレート
    duration = 1  # 秒
    random_signal = np.random.rand(sr * duration)

    # JITコンパイルを初期化
    _, _ = librosa.beat.beat_track(y=random_signal, sr=sr)

    print("start!")
    while True:
        frames, samp_rate = rec(dev_index)
        if IsMusicPlaying(frames):
            bpm, beats_delay = get_bpm(frames, samp_rate)
            print("BPM:", bpm)
            maracas_controller.update_bpm(bpm, beats_delay)
            maracas_controller.start()
        else:
            maracas_controller.stop()

if __name__ == "__main__":
    test()