import time
import hashlib
import json
from collections import namedtuple

class AdvancedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__jsonencode__'):
            return obj.__jsonencode__()
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)

class Block(object):
    def __init__(self, Height, transaction, PrevBlockHash=''):
        self.transaction = transaction
        self.PrevBlockHash = PrevBlockHash
        self.time = int(time.time())
        self.Height = Height
        self.Nonce = 0
        self.bits = 8
        self.data = self.transaction+str(self.PrevBlockHash)+str(self.time)
        self.Hash = self.setHash()

    def setHash(self):
        self.Hash = hashlib.sha256(
            (self.transaction+str(self.PrevBlockHash)+str(self.time) + str(self.Nonce)).encode('utf-8')).hexdigest()

    def mine(self):
        self.Hash = hashlib.sha256(
            (self.transaction+str(self.PrevBlockHash)+str(self.time) + str(self.Nonce)).encode('utf-8')).hexdigest()

        while int(self.Hash,16)>>(256-self.bits):
            self.Nonce += 1 
            self.Hash = hashlib.sha256(
                (self.transaction+str(self.PrevBlockHash)+str(self.time) + str(self.Nonce)).encode('utf-8')).hexdigest()
            print(self.Hash, '\r'*64, end='')

        print("block mined :", self.Hash)

    # def toJSON(self):
    #     # print(json.dumps(self, default=lambda o: o.__dict__, sort_keys=False, indent=4))
    #     return json.dumps(self, default=lambda o: o.__dict__)
    def __jsonencode__(self):
        return json.dumps(self, default=lambda o: o.__dict__,indent=2)
    

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


    def toDB(self):
        
        with open ('./ShenCoin.json','w') as json_file:
            json_file.write(json.dumps(self.chain,cls=AdvancedJSONEncoder,indent=2))

    def readDB(self,path):
        with open (path,'r') as json_file:
            data = json.load(json_file)
            for i in data:
                self.chain.append(json.loads(i, object_hook=lambda d: namedtuple('X', d.keys())(*d.values())))
                print(self.chain[-1].Hash)
                

def main():

    a = Blockchain()
    a.readDB('./ShenCoin.json')


if __name__ == '__main__':
    main()
