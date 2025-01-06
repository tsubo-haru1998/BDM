from process_music import rec, get_bpm, IsMusicPlaying
from demo_servo import MaracasController

def test():
    dev_index = 2 # マイクのデバイス番号。調べる必要あり

    maracas_controller = MaracasController()

    while True:
        frames, samp_rate = rec(dev_index)
        if IsMusicPlaying(frames):
            bpm, beats_delay = get_bpm(frames, samp_rate)
            maracas_controller.update_bpm(bpm, beats_delay)
            maracas_controller.start()
        else:
            maracas_controller.stop()

if __name__ == "__main__":
    test()