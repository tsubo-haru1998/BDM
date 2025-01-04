from process_music import get_music, get_bpm, IsMusicPlaying
from demo_servo import MaracasController

def test():
    dev_index = 2 # マイクのデバイス番号。調べる必要あり
    samp_rate = 48000 # サンプリング周波数

    maracas_controller = MaracasController()

    while True:
        frames = get_music(dev_index, samp_rate)
        if IsMusicPlaying(frames):
            bpm, beats_time = get_bpm(frames, samp_rate)
            maracas_controller.update_bpm(bpm, beats_time)
            maracas_controller.start()
        else:
            maracas_controller.stop()

if __name__ == "__main__":
    test()