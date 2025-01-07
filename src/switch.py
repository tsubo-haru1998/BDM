# -*- coding: utf-8 -*-
import pigpio
import os
import time
import signal

# GPIOピン番号
BUTTON_PIN = 15
GET_READY_LED_PIN = 17


# 状態を管理する変数
running = False  # プログラムが実行中かどうか
program_pid = None  # 実行中プログラムのPID

def toggle_program(gpio, level, tick):
    """ボタンが押されたときにプログラムの開始・停止を切り替える"""
    global running, program_pid

    if running:
        # プログラム停止
        if program_pid is not None:
            print("プログラムを停止します...")
            os.kill(program_pid, signal.SIGTERM)
            os.waitpid(program_pid, 0) # プロセス終了まで待機
            program_pid = None
        running = False
        pi.write(GET_READY_LED_PIN, False)

    else:
        # プログラム開始
        print("プログラムを開始します...")
        program_pid = os.fork()
        if program_pid == 0:
            # 子プロセスで別プログラムを実行
            os.execlp("python3", "python3", "BDM/src/test.py", str(GET_READY_LED_PIN))  # 実行したいプログラム
        running = True

# pigpioインスタンス作成
pi = pigpio.pi()
if not pi.connected:
    print("pigpioデーモンが起動していません。sudo pigpiodを実行してください。")
    exit()

# GPIO設定
pi.set_mode(BUTTON_PIN, pigpio.INPUT)
pi.set_pull_up_down(BUTTON_PIN, pigpio.PUD_UP)
pi.set_glitch_filter(BUTTON_PIN, 30000) # ノイズにより複数回コールバックが呼ばれるのを防ぐ対策で30msのデバウンズを設ける

pi.set_mode(GET_READY_LED_PIN, pigpio.OUTPUT)
pi.write(GET_READY_LED_PIN, False)

# ボタンのコールバック設定
pi.callback(BUTTON_PIN, pigpio.FALLING_EDGE, toggle_program)

# メインループ
try:
    print("ボタンを押してプログラムの開始・停止を切り替えてください（CTRL+Cで終了）")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n終了中...")
    if running and program_pid is not None:
        os.kill(program_pid, signal.SIGTERM)
        os.waitpid(program_pid, 0)
finally:
    pi.write(GET_READY_LED_PIN, False)
    pi.stop()

    