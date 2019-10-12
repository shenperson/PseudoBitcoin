from PseudoBitcoin import Blockchain

mining_reward = 100
# reward of mining a new block


class TXInput(object):
    def __init__(self, Txid, Vout, ScriptSig):
        self.Txid = Txid
        self.Vout = Vout
        self.ScriptSig = ScriptSig


class TXOutput(object):
    def __init__(self, Value, ScriptPubKey):
        self.Value = Value
        self.ScriptPubKey = ScriptPubKey
        self.spent = False


class Transaction(object):
    def __init__(self, ID, Vin, Vout):
        self.ID = ID
        self.Vin = Vin
        self.Vout = Vout

    def searchName(self, name):
        find = False
        out = False
        acc = 0
        for i in self.Vin:
            if i.ScriptSig == name:
                find = True
                acc -= i.Vout
        for i in self.Vout:
            if i.ScriptPubKey == name:
                find = True
                acc += i.Value
                if not i.spent:
                    out = True
        return find, out, acc

    def toStr(self):
        tx = str(self.ID)+':Vin{'
        for i in self.Vin:
            tx += str(i.Txid)+','+str(i.Vout)+i.ScriptSig
        tx += '},Vout{'
        for i in self.Vout:
            tx += str(i.Value)+i.ScriptPubKey
        tx += '}'
        return tx


class newCoinbaseTX(object):
    def __init__(self, ID, to_addr, data=''):
        txin = TXInput([], -1, data)
        txout = TXOutput(mining_reward, to_addr)
        self.tx = Transaction(ID, [txin], [txout])


class utxoTX(object):
    def __init__(self, to_addr, from_addr, amount, utxo_set):
        inputs = []
        outputs = []
        acc, valid_outputs = utxo_set.find_spendable_outputs(amount)
        if acc < amount:
            print('No enough funds')

        outputs.append(TXOutput(amount, to_addr))
        if acc > amount:
            outputs.append(TXOutput(acc-amount, from_addr))
        self._tx = Transaction(None, inputs, outputs)
        self._utxo_set = utxo_set


class UTXOSet(object):
    def __init__(self, blockchain):
        self.blockchain = blockchain.chain

    # def findUTXO(self):
    #     utxo = []
    #     for


def test():
    a = newCoinbaseTX('me', 'hi')
    print(len(a.Vin))


if __name__ == '__main__':
    test()
