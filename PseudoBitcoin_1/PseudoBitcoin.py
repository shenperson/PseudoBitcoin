import time
import hashlib


class Block(object):
    def __init__(self, Height, transaction, PrevBlockHash=''):
        self.transaction = transaction
        self.PrevBlockHash = PrevBlockHash
        self.time = int(time.time())
        self.Height = Height
        self.Nonce = 0
        self.bits = 16
        self.data = self.transaction+str(self.PrevBlockHash)+str(self.time)
        self.Hash = self.setHash()

    def setHash(self):
        self.Hash = hashlib.sha256(
            (self.data + str(self.Nonce)).encode('utf-8')).hexdigest()
        print(type(self.Hash))

    def mine(self):
        while  (int(hashlib.sha256(
                (self.data + str(self.Nonce)).encode('utf-8')).hexdigest(), 16) & (int('1'*self.bits) << (256-self.bits))):
            self.Nonce += 1
            # self.setHash()
            self.Hash = hashlib.sha256(
                (self.data + str(self.Nonce)).encode('utf-8')).hexdigest()
            print(self.Hash, '\r'*64, end='')

        print("block mined :", self.Hash)


class Blockchain(object):
    def __init__(self):
        self.chain = []

    def addGenesisBlock(self, transaction):
        newBlock = Block(0, transaction, '')
        newBlock.mine()
        self.chain.append(newBlock)

    def addBlock(self, transaction):
        prevBlock = self.chain[-1]
        newBlock = Block(len(self.chain), transaction, prevBlock.Hash)
        newBlock.mine()
        self.chain.append(newBlock)


def main():
    a = Blockchain()
    a.addGenesisBlock('as')
    a.addBlock('ass')


if __name__ == '__main__':
    main()
