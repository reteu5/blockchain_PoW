import hashlib
import datetime
import json
import random
import nodelib

nodes = []
nodeCount = 5
limit = 15

def getGenBlock():
    block = {
        'ver': 1,
        'prev_hash': '',
        'mrkl_root': '',
        'time': datetime.datetime.now().timestamp(),
        'bits': 1,
        'nonce': 0,
        'transactions': []
    }

    difficulty = (64 - block['bits']) * 'f'

    while True:
        hash = hashlib.sha256(json.dumps(block).encode()).hexdigest()

        if int(hash, 16) < int(difficulty, 16):
            break

        block['nonce'] += 1

    return block

def init():
    genBlock = getGenBlock()

    for i in range(0, nodeCount):
        node = nodelib.Miner()
        node.address = hashlib.sha256(str(i).encode()).hexdigest()
        node.recvBlock(genBlock)
        nodes.append(node)

def broadcastTransaction(transaction):
    # nodes는 init에서 정의된 전역변수
    for i, node in enumerate(nodes):
        node.recvTransaction(transaction)

    return True

def broadcastBlock(block):
    # nodes는 init에서 정의된 전역변수
    for i, node in enumerate(nodes):
        node.recvBlock(block)

    return True


init()
repeat = 0
while repeat < limit:
    print("[+] transactions ---------")
    for i, node in enumerate(nodes):
        if random.randint(0, 1) >= 0:
            sender = node
            
            if sender.balance < 1:
                continue

            sel = i
            while sel == i:
                sel = random.randint(0, len(nodes) - 1)

            
            to = nodes[sel]
            amount = random.randint(1, sender.balance)

            transaction = sender.sendTo(to.address, amount)
            broadcastTransaction(transaction)

            print("$ ", amount, "from [" + str(i) + "]", sender.address[0:10] + "...",
                  "to [" + str(sel) + "]", to.address[0:10] + "...")
            


    sel = random.randint(0, nodeCount - 1)
    miner = nodes[sel]
    candBlock = miner.doMining()
    if broadcastBlock(candBlock):
        print("[+] Mining by ", "[" + str(sel) + "] ", repeat + 1, " --------- ",
              datetime.datetime.fromtimestamp(candBlock['time']))
        print("hash: ", hashlib.sha256(json.dumps(candBlock).encode()).hexdigest())
        print("nonce: ", candBlock['nonce'])
        print("bits: ", candBlock['bits'])


    print("[+] balance ---------")
    for i, node in enumerate(nodes):
        if node.balance > 0:
            print("[" + str(i) + "]", node.address[0:10] + "...", "$ ", node.balance)

    
    print()
    repeat += 1

for block in nodes[0].chain:
    print(block)