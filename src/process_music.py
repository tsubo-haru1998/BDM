import sounddevice as sd
import librosa
import numpy as np

def rec(dev_index):
    record_secs = 2 # 録音時間[s]

    sd.default.device = [dev_index, None] # Input, Outputデバイス指定
    input_device_info = sd.query_devices(device=sd.default.device[0])
    sr_in = int(input_device_info["default_samplerate"]) # Input Device(Mic.)のサンプリングレート

    # 録音
    myrecording = sd.rec(int(record_secs * sr_in), samplerate=sr_in, channels=1) # ndarray, size=(samp_rate * record_secs, channels), 各データは-1~1の値を取る
    sd.wait() # 録音終了待ち
    myrecording = np.squeeze(myrecording) # 2次元配列なので1次元にする

    return myrecording, sr_in

def get_bpm(y, samp_rate):
    print("getting bpm")
    # BPMと拍のタイミングを共に配列で取得
    bpm, beats = librosa.beat.beat_track(y=y, sr=samp_rate)
    print("got bpm")
    # 録音し始めたタイミングと拍のタイミングのずれを秒単位で取得
    if len(beats) > 0:
        beats_delay = librosa.frames_to_time(beats, sr=samp_rate)[0]
    else:
        beats_delay = 0.0
    # 返り値は共にfloat32
    return bpm.item(), beats_delay

def IsMusicPlaying(y):
    # 音楽が流れているかどうか判断する
    threshold = 2**-7
    # 録音データの二乗平均値を算出
    rms = np.sqrt(np.mean(y**2))
    print("rms:", rms)
    # thresholdよりもrmsが大きければ音楽が流れていると判断
    return rms > threshold