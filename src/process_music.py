import pyaudio
import librosa
import numpy as np

def get_music(dev_index, samp_rate):
    # dev_indexで指定したデバイス（マイク）の音を取得する
    form_1 = pyaudio.paInt16
    chans = 1
    samp_rate = 44100
    chunk = 1024
    record_secs = 2

    audio = pyaudio.PyAudio()

    stream = audio.open(format=form_1, rate=samp_rate, channels=chans, input_device_index=dev_index, input=True, frames_per_buffer=chunk)

    frames = np.empty(0, chans)
    for _ in range(0, int((samp_rate / chunk) * record_secs)):
        data = stream.read(chunk)
        ndarray = np.frombuffer(data, dtype='int16')
        frames = np.hstack((frames, ndarray))

    stream.stop_stream()
    stream.close()
    audio.terminate()

    return frames

def get_bpm(y, samp_rate):
    bpm, beats = librosa.beat.beat_track(y=y, sr=samp_rate)
    # beatsを秒単位に換算
    beats_time = librosa.frames_to_time(beats, sr=samp_rate)
    return bpm, beats_time

def IsMusicPlaying(y: np.ndarray):
    # もし音量の二乗平均がthresholdを超えたらそれは音楽が流れていると判断
    threshold = 100

    rms = np.sqrt(np.mean(y**2))

    return rms > threshold