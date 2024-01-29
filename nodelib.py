import hashlib
import json
import time
class Node:
    def __init__(self):
        self.address = 0
        self.balance = 0
        self.isMiner = False
        self.chain = []
        self.transactions = []

    def proof(self, block):
        difficulty = (64 - block['bits']) * 'f'

        hash = hashlib.sha256(json.dumps(block).encode()).hexdigest()
        if int(hash, 16) < int(difficulty, 16):
            return True
        
        return False
    
    def calBalance(self, transaction): 
        if transaction['from'] == self.address:
            self.balance -= transaction['amount']
        elif transaction['to'] == self.address:
            self.balance += transaction['amount']

        return True
    
    def recvBlock(self, block):
        res = self.proof(block)

        # genesis block이 아니며, 이미 체인에 추가된 블록이라면 False
        if len(self.chain) > 0 and self.chain[-1]['prev_hash']  == block['prev_hash']:
            return False
        
        if res:
            self.chain.append(block)
            
        
        self.transactions = []
        # 나와 연관되어있는 트랜잭션들을 찾아서 소화
        for transaction in block['transactions']:
            self.calBalance(transaction)

        return True
    
    def recvTransaction(self, transaction):
        sender = transaction['from']
        amount = transaction['amount']
        
        if sender == self.address:
            if amount > self.balance:
                return False
            
        self.transactions.append(transaction)

        return True
    
    def sendTo(self, to, amount):
        transaction = {
            'from': self.address,
            'to': to,
            'amount': amount
        }

        return transaction
    
class Miner(Node):
    def __init__(self):
        super().__init__()
        self.isMiner = True

    def getLeafs(self, transactions):
        res = []
        for i in range(0, len(transactions)):
            hash = hashlib.sha256(json.dumps(transactions[i]).encode()).hexdigest()

            res.append(hash)
        
        return res
    
    def getMrklRoot(self, transactions):
        leafs = self.getLeafs(transactions)

        if len(leafs) <= 0:
            return ''
        elif len(leafs) == 1:
            return leafs[0]
        
        while len(leafs) > 1:
            hashA = leafs.pop(0)
            hashB = leafs.pop(0)
            hashC = hashlib.sha256(''.join([hashA, hashB]).encode()).hexdigest()
            leafs.append(hashC)

    def doMining(self):
        prevTime = self.chain[len(self.chain) - 1]['time']
        now = time.time()

        fcount = 64 - self.chain[len(self.chain) - 1]['bits']
        if now - prevTime > 5:
            fcount = (fcount + 1) if fcount < 64 else fcount
        else:
            fcount = (fcount - 1) if fcount > 0 else fcount

        difficulty = fcount * 'f'

        prevHash = ''

        if len(self.chain) > 0:
            prevBlock = self.chain[len(self.chain) - 1]
            prevHash = hashlib.sha256(json.dumps(prevBlock).encode()).hexdigest()

        self.recvTransaction({
            'from': 'None',
            'to': self.address,
            'amount': 50
        })

        block = {
            'ver': 1,
            'prev_hash': prevHash,
            'mrkl_root': self.getMrklRoot(self.transactions),
            'time': now,
            'bits': 64 - fcount,
            'nonce': 0,
            'transactions': self.transactions
        }

        while True:
            hash = hashlib.sha256(json.dumps(block).encode()).hexdigest()
            if int(hash, 16) < int(difficulty, 16):
                break

            block['nonce'] += 1

        return block