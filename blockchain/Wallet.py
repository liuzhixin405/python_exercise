import rsa

class Wallet:
    def __init__(self):
        self.public_key,self.private_key =rsa.newkeys(512)

    def get_balance(self,blockchain):
        balance = 0
        for block in blockchain.chain:
            for transaction in block.data:
                if 'recipient' in transaction and transaction['recipient'] == self.public_key:
                    balance += transaction['amount']
                if 'sender' in transaction and transaction['sender'] == self.public_key:
                    balance -=transaction['amount']
        return balance
    
    def send_transaction(self,recipient,amount,blockchain):
        if self.get_balance(blockchain) >= amount:
            blockchain.add_transaction(self.public_key,recipient,amount)