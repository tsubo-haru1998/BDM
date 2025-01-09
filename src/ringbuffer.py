import numpy as np

class NumPyRingBuffer:
    def __init__(self, size, dtype=np.float32):
        """
        リングバッファを初期化
        :param size: バッファの最大サイズ
        :param dtype: データ型 (例: np.float32, np.int32)
        """
        self.buffer = np.zeros(size, dtype=dtype)
        self.size = size
        self.start = 0
        self.end = 0
        self.full = False

    def extend(self, data):
        """
        データをバッファに追加
        :param data: 新しく追加するデータ（スカラーまたは配列）
        """
        if np.isscalar(data):  # スカラーの場合
            data = np.array([data], dtype=self.buffer.dtype)
        else:  # 配列の場合
            data = np.array(data, dtype=self.buffer.dtype)

        for value in data:
            self.buffer[self.end] = value
            self.end = (self.end + 1) % self.size
            if self.full:
                self.start = (self.start + 1) % self.size
            elif self.end == self.start:
                self.full = True

    def get(self):
        """
        現在のバッファ内容を取得
        順序が整っている状態で返す
        """
        if self.full:
            return np.concatenate((self.buffer[self.start:], self.buffer[:self.start]))
        else:
            return self.buffer[self.start:self.end]

    def clear(self):
        """
        バッファをクリア
        """
        self.buffer[:] = 0
        self.start = 0
        self.end = 0
        self.full = False

    def __len__(self):
        """
        バッファ内の有効なデータ数を返す
        """
        if self.full:
            return self.size
        elif self.end >= self.start:
            return self.end - self.start
        else:
            return self.size - self.start + self.end