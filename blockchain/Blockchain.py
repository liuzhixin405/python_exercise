from Block import Block

class Blockchain:       # 区块链
    def __init__(self):
        self.chain = [self.create_genessis_block()]        # Block 数组
    def create_genessis_block(self):
        return Block("Genesis Block","0")
    
    def add_block(self,data):
        previous_block = self.chain[-1]
        new_block=Block(data,previous_block.hash)
        self.chain.append(new_block)

    def validate_chain(self):
        for i in range(1,len(self.chain)):
            current_block = self.chain[i]
            previous_block=self.chain[i-1]
            if current_block.hash!=current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True