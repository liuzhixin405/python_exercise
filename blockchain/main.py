from Blockchain import Blockchain
from Cryptocurrency import Cryptocurrency
from Wallet import Wallet


if __name__ =="__main__":
    blockchain=Blockchain()
    blockchain.add_block("t 1")
    blockchain.add_block("t 2")

    print("区块链是否有效:", blockchain.validate_chain())

    cryptocurrency = Cryptocurrency()
    cryptocurrency.create_genesis_block()

    wallet1 = Wallet()
    wallet2 = Wallet()

    cryptocurrency.add_transaction(wallet1.public_key,wallet2.public_key,10)
    cryptocurrency.mine_block(wallet1.public_key)

    print("账户1余额:", wallet1.get_balance(cryptocurrency))
    print("账户2余额:", wallet2.get_balance(cryptocurrency))
