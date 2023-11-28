from Block import Block


class Cryptocurrency:
    def __init__(self):
        self.chain=[]
        self.pending_transactions=[]

    def create_genesis_block(self):
        genesis_block = Block("Genesis Block","0")
        self.chain.append(genesis_block)

    def mine_block(self,miner_address):
        block_data="Block reward + "+str(miner_address)
        self.pending_transactions.append(block_data)
        previous_block = self.chain[-1]
        new_block = Block(self.pending_transactions,previous_block.hash)
        self.chain.append(new_block)
        self.pending_transactions=[]

    def add_transaction(self,sender,recipient,amount):
        transaction = {
          'sender': sender,
            'recipient': recipient,
            'amount': amount
        }
        self.pending_transactions.append(transaction)
    
