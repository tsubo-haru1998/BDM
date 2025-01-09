import sounddevice as sd
import librosa
import numpy as np

def rec_from_stream(audio_buffer, samp_rate):
    # コールバック関数(音声データをリングバッファに格納)
    def callback(indata, frames, time, status):
        if status:
            print(status)
        audio_buffer.extend(indata[:, 0])  # 受け取った音声データをキューに格納(bpmを求められるようモノラルにする)

    # 録音開始のためのストリーム
    stream = sd.InputStream(callback=callback, channels=1, samplerate=samp_rate, blocksize=8192)
    stream.start()
    return stream

def get_bpm(y, samp_rate):
    # BPMと拍のタイミングを共に配列で取得
    bpm, beats = librosa.beat.beat_track(y=y, sr=samp_rate, tightness=200)
    # 録音し始めたタイミングと拍のタイミングのずれを秒単位で取得
    if len(beats) > 0:
        beats_delay = librosa.frames_to_time(beats, sr=samp_rate)[0]
    else:
        beats_delay = 0.0
    # 返り値は共にfloat32
    return bpm.item(), beats_delay

def get_volume(y):
    # 音量(録音データの二乗平均値)を取得
    if y.size > 0:
        rms = np.sqrt(np.mean(y**2))
    else:
        rms = 0  # または適切なデフォルト値
    print("rms:", rms)
    return rms