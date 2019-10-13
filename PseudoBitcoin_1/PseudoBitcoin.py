import time
import hashlib
import json
from collections import namedtuple
import sys
import UTXO
import os

BITS = 8


class AdvancedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__jsonencode__'):
            return obj.__jsonencode__()
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


class Block(object):
    def __init__(self, Height: int, transaction: list, PrevBlockHash='', time=int(time.time()), Nonce=0, bits=BITS, Hash='', tx=''):
        self.transaction = transaction
        self.tx = tx
        for i in transaction:
            self.tx += i.toStr()
        self.PrevBlockHash = PrevBlockHash
        self.time = time
        self.Height = Height
        self.Nonce = Nonce
        self.bits = BITS
        self.Hash = Hash

    @classmethod
    def fromJSON(cls, data) -> 'Block':
        block = json.loads(data, object_hook=lambda d: namedtuple(
            'X', d.keys())(*d.values()))
        txs = []
        for tx in block.transaction:
            txs.append(UTXO.Transaction.fromJSON(tx))

        return cls(transaction=txs, Height=block.Height, time=block.time, Nonce=block.Nonce, bits=block.bits, PrevBlockHash=block.PrevBlockHash, Hash=block.Hash, tx=block.tx)

    def setHash(self):
        self.Hash = hashlib.sha256(
            (self.tx+str(self.PrevBlockHash)+str(self.time) + str(self.Nonce)).encode('utf-8')).hexdigest()

    def mine(self):
        self.Hash = hashlib.sha256(
            (self.tx+str(self.PrevBlockHash)+str(self.time) + str(self.Nonce)).encode('utf-8')).hexdigest()

        while int(self.Hash, 16) >> (256-self.bits):
            self.Nonce += 1
            self.Hash = hashlib.sha256(
                (self.tx+str(self.PrevBlockHash)+str(self.time) + str(self.Nonce)).encode('utf-8')).hexdigest()
            print(self.Hash, '\r'*64, end='')
        print("block mined :"+' '*52)
        self.print()

    def __jsonencode__(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=2)

    def print(self):
        print('{')
        print('  Height :', self.Height)
        print('  Time :', self.time)
        print('  Transaction :', self.tx)
        print('  PrevBlockHash :', self.PrevBlockHash)
        print('  Hash :', self.Hash)
        print('},')


class Blockchain(object):
    def __init__(self):
        self.chain = []

    # add block
    def addGenesisBlock(self, ID, miner):
        # newBlock = Block(0, transaction, '')
        newBlock = Block(0, [UTXO.newCoinbaseTX(ID, miner).tx], '')
        newBlock.mine()
        self.chain.append(newBlock)

    def addBlock(self, transaction):

        prevBlock = self.chain[-1]
        newBlock = Block(len(self.chain), transaction, prevBlock.Hash)
        newBlock.mine()
        self.chain.append(newBlock)

    # DB
    def writeDB(self, path):
        with open(path, 'w') as json_file:
            json_file.write(json.dumps(
                self.chain, cls=AdvancedJSONEncoder, indent=2))

    def readDB(self, path):
        with open(path, 'r') as json_file:
            data = json.load(json_file)
            for i in data:
                self.chain.append(Block.fromJSON(i))

    # print
    def print(self):
        for i in self.chain:
            i.print()

    # check
    def isValid(self):
        if len(self.chain) > 1:
            for i, block in enumerate(self.chain[:-2]):
                if self.chain[i+1].PrevBlockHash != block.Hash:
                    return False
            return True
        return True

    # UTXO
    def findUTXO(self, name):
        utxo = []
        acc = 0
        for i in self.chain:
            for tx in i.transaction:
                find, out, _acc = tx.searchName(name)
                if find:
                    acc += _acc
                if out:
                    utxo.append(tx)

        return acc, utxo

    def check(self, txi, txo, from_addr):
        acc, utxo = self.findUTXO(from_addr)
        for tx in utxo:
            for vo in tx.Vout:
                if vo.ScriptPubKey == from_addr:
                    txi.append(UTXO.TXInput(tx.ID, vo.Value, from_addr))
                    vo.spent = True
        if acc < txo[0].Value:
            print('No enough funds')
            return False
        if acc > txo[0].Value:
            txo.append(UTXO.TXOutput(acc - txo[0].Value, from_addr))
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


def cli():
    filename = './ShenCoin.json'
    if len(sys.argv) < 2:
        printUsage()
    else:
        blockchain = Blockchain()
        if sys.argv[1] == 'addblock' and len(sys.argv) == 4 and (sys.argv[2] == '-transaction' or sys.argv[2] == '-t'):
            blockchain.readDB(filename)
            blockchain.addBlock(sys.argv[3])
            blockchain.writeDB(filename)

        elif sys.argv[1] == 'createblockchain' and len(sys.argv) == 4 and sys.argv[2] == '-address':
            if os.stat(filename).st_size:
                blockchain.readDB(filename)
                print('Blockchain has been already created. Please try another command')
            else:
                blockchain.addGenesisBlock('TX0', sys.argv[3])
                blockchain.writeDB(filename)

        elif sys.argv[1] == 'getbalance' and len(sys.argv) == 4 and sys.argv[2] == '-address':
            if not os.stat(filename).st_size:
                print(
                    'Blockchain has not been created. Please create a blockchain first')
            blockchain.readDB(filename)
            acc, utxo = blockchain.findUTXO(sys.argv[3])
            if not len(utxo):
                print('No transaction record')
            print('Balance of {0}: {1}'.format(sys.argv[3], acc))

        elif (sys.argv[1] == 'printchain'):
            if not  os.stat(filename).st_size:
                print('Blockchain has not been created. Please create a blockchain first')
                return
            blockchain.readDB(filename)
            blockchain.print()

        elif (sys.argv[1] == 'printblock') and len(sys.argv) == 4 and (sys.argv[2] == '-height' or sys.argv[2] == '-h'):
            if not os.stat(filename).st_size:
                print('Blockchain has not been created. Please create a blockchain first')
                return
            blockchain.readDB(filename)
            try:
                blockchain.chain[int(sys.argv[3])].print()
            except:
                print('Please enter a number less than the height({})'.format(
                    len(blockchain.chain)))

        elif len(sys.argv) == 8 and sys.argv[1] == 'send' and sys.argv[2] == '-from' and sys.argv[4] == '-to' and sys.argv[6] == '-amount':
            if not os.stat(filename).st_size:
                print('Blockchain has not been created. Please create a blockchain first')
                return
            try:
                amount = int(sys.argv[7])
                blockchain.readDB(filename)
                txid = len(blockchain.chain)
                
                if addNewTX(blockchain, sys.argv[3], sys.argv[5], amount, txid):
                    blockchain.writeDB(filename)
            except:
                print('Please enter a number after -amount')

        elif sys.argv[1] == 'clear':
            print('Clear database')
            with open(filename, "r+") as f:
                f.seek(0)
                f.truncate()
        else:
            printUsage()


def addNewTX(bc, from_addr, to_addr, amount, txid):
    txi = []
    txo = [UTXO.TXOutput(amount, to_addr)]

    if bc.check(txi, txo, from_addr):
        tx1 = UTXO.Transaction('TX'+str(txid), txi, txo)
        bc.addBlock([tx1])
        txid += 1
        return True


def test3():
    a = Blockchain()
    a.addGenesisBlock('TX00', 'Alice')
    txid = 1
    addNewTX(a, 'Alice', 'Bob', 10, txid)
    addNewTX(a, 'Bob', 'Cat', 10, txid)
    addNewTX(a, 'Apple', 'Alice', 10, txid)
    addNewTX(a, 'Alice', 'Dad', 10, txid)


if __name__ == '__main__':
    cli()
