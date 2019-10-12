import time
import hashlib
import json
from collections import namedtuple
import sys
import UTXO

BITS = 8

class AdvancedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__jsonencode__'):
            return obj.__jsonencode__()
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)

class Block(object):
    def __init__(self, Height:int, transaction:list,PrevBlockHash='',time=int(time.time()),Nonce=0,bits=BITS,Hash=''):
        self.transaction = transaction
        self.tx = ''
        for i in transaction:
            self.tx += i.toStr()
        self.PrevBlockHash = PrevBlockHash
        self.time = time
        self.Height = Height
        self.Nonce = Nonce
        self.bits = BITS
        self.Hash = Hash

    @classmethod
    def fromJSON(cls,data) -> 'Block':
        block = json.loads(data, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
        return cls(transaction=block.transaction,Height=block.Height,time=block.time,Nonce=block.Nonce,bits=block.bits,PrevBlockHash=block.PrevBlockHash,Hash=block.Hash)

    def setHash(self):
        self.Hash = hashlib.sha256(
            (self.tx+str(self.PrevBlockHash)+str(self.time) + str(self.Nonce)).encode('utf-8')).hexdigest()

    def mine(self):
        self.Hash = hashlib.sha256(
            (self.tx+str(self.PrevBlockHash)+str(self.time) + str(self.Nonce)).encode('utf-8')).hexdigest()

        while int(self.Hash,16)>>(256-self.bits):
            self.Nonce += 1 
            self.Hash = hashlib.sha256(
                (self.tx+str(self.PrevBlockHash)+str(self.time) + str(self.Nonce)).encode('utf-8')).hexdigest()
            print(self.Hash, '\r'*64, end='')
        print("block mined :"+' '*52)
        self.print()

    def __jsonencode__(self):
        return json.dumps(self, default=lambda o: o.__dict__,indent=2)

    def print(self):
        print('{')
        print('  Height :',self.Height)
        print('  Time :',self.time)
        print('  Transaction :',self.tx)
        print('  PrevBlockHash :',self.PrevBlockHash)
        print('  Hash :',self.Hash)
        print('},')    
    

class Blockchain(object):
    def __init__(self):
        self.chain = []
    
    ### add block
    def addGenesisBlock(self,ID, miner):
        # newBlock = Block(0, transaction, '')
        newBlock = Block(0, [UTXO.newCoinbaseTX(ID,miner).tx], '')
        newBlock.mine()
        self.chain.append(newBlock)

    def addBlock(self, transaction):

        prevBlock = self.chain[-1]
        newBlock = Block(len(self.chain), transaction, prevBlock.Hash)
        newBlock.mine()
        self.chain.append(newBlock)

    ### DB
    def writeDB(self,path):
        with open (path,'w') as json_file:
            json_file.write(json.dumps(self.chain,cls=AdvancedJSONEncoder,indent=2))

    def readDB(self,path):
        with open (path,'r') as json_file:
            data = json.load(json_file)
            for i in data:
                self.chain.append(Block.fromJSON(i))

    ### print 
    def print(self):
        for i in self.chain:
            i.print()

    ### check
    def isValid(self):
        if len(self.chain)>1:
            for i,block in enumerate(self.chain[:-2]):
                if self.chain[i+1].PrevBlockHash != block.Hash:
                    return False
            return True
        return True
    
    ### UTXO
    def findUTXO(self,name):
        utxo = []
        acc = 0
        for i in self.chain:
            for tx in i.transaction:
                find,out,_acc = tx.searchName(name)
                if find:
                    acc += _acc
                if out:
                    utxo.append(tx)

        return acc, utxo

    def check(self,txi,txo,name):
        acc , utxo = self.findUTXO(name)
        for tx in utxo:
            for vo in tx.Vout:
                if vo.ScriptPubKey == name:
                    txi.append(UTXO.TXInput(tx.ID,vo.Value,name))
                    vo.spent =True
        if acc < txo[0].Value:
            print('No enough funds')
            return False
        if acc > txo[0].Value:
            txo.append(UTXO.TXOutput(acc - txo[0].Value,name))
        return True


def test1():
    a = Blockchain()
    a.readDB('./ShenCoin.json')
    a.addBlock('B give C $20')
    a.print()
    print(a.isValid())

def printUsage():
    print('usage:')
    print('    python PseudoBitcoin.py addblock transaction { \"blablabla\" }')
    print('    python PseudoBitcoin.py printchain')
    print('    python PseudoBitcoin.py printblock height { height }')

def test2():
    if len(sys.argv) < 2:
        printUsage()
    else:
        filename = './ShenCoin.json'
        blockchain = Blockchain()
        blockchain.readDB(filename)
        if sys.argv[1] == 'addblock' and len(sys.argv) == 4 and (sys.argv[2] ==  '-transaction' or sys.argv[2] == '-t'):
            blockchain.addBlock(sys.argv[3])
            blockchain.writeDB(filename)

        elif (sys.argv[1] == 'printchain'):
            blockchain.print()
            
        elif (sys.argv[1] == 'printblock') and len(sys.argv) == 4 and (sys.argv[2] ==  '-height' or sys.argv[2] == '-h'):
            try:
                blockchain.chain[int(sys.argv[3])].print()
            except:
                print('Please enter a number less than the height({})'.format(len(blockchain.chain)))

        elif sys.argv[1]=='clear':
            pass
        else:
            printUsage()

def test3():
    a = Blockchain()
    a.addGenesisBlock('TX00','Alice')

    txi = []
    txo = [UTXO.TXOutput(10, 'Bob')]
    
    if a.check(txi,txo, 'Alice'):
        tx1 = UTXO.Transaction('TX01',txi,txo)
        a.addBlock([tx1])

    txi = []
    txo = [UTXO.TXOutput(5, 'Cat')]
    if a.check(txi, txo, 'Bob'):
        tx1 = UTXO.Transaction('TX02', txi, txo)
        a.addBlock([tx1])
    
    txi = []
    txo = [UTXO.TXOutput(5, 'Cat')]
    if a.check(txi, txo, 'Alice'):
        tx1 = UTXO.Transaction('TX03', txi, txo)
        a.addBlock([tx1])

if __name__ == '__main__':
    test3()
