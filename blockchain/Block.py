import hashlib
import time

class Block:
    def __init__(self,data,previous_hash):
        self.timestamp=time.time()  # 创建时间
        self.data = data            # 当前数据
        self.previous_hash = previous_hash  # 前一个hash
        self.hash = self.calculate_hash()   # 当前hash

    def calculate_hash(self):     # 创建hash
        data = str(self.timestamp)+str(self.data)+str(self.previous_hash)
        return hashlib.sha256(data.encode()).hexdigest()
        