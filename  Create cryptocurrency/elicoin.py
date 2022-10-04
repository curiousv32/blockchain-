#Module 2  -create a cryptocurrency
# to be installed
#Flask==0.12.2 :pip install Flask==0.12.2
#postman HTTP client: https://www.getpostman.com/ 
#requests==2.18.4: pip install requests==2.18.4

import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

#part 1 -building a Blockchain


class Blockchain:
    
    
    def __init__(self):#class object instance
        self.chain = []#chain that contains the block list
        self.transactions =[] #creates the list of transactions to be appended to the block
        self.create_block(proof = 1,previous_hash ='0')#genesis block (each block has its proof,link with the previous block)
        self.nodes = set()
   
    
    def create_block(self, proof,previous_hash):#(uses the variables  of the object,proof to show it has been mined,previous hash that links it all)
       block ={'index': len(self.chain) + 1,
                'timestamp' : str(datetime.datetime.now()),
                'proof': proof,
                'previous_hash' :previous_hash,
                'transactions' : self.transactions
                }#dictionary keys to hold the characteristics of the block{index,time when the block was mined,proof,previous hash,anything else}
       
       self.transactions = [] #empties the list of transactions since it is already added to the block
       self.chain.append(block)
       return block
   
    
    def get_previous_block(self):
        return self.chain[-1]#returns the previous block[the last block in the chain]
    
 
#the proof of work is a problem/function that the miners solve .it is 
#easy to verify but hard to solve    
    def proof_of_work(self,previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()#hash_operation that gets the hash
            if hash_operation[:4] == '0000':#character should start with four zeros
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    def hash(self, block):#hashes each block
        encoded_block = json.dumps(block, sort_keys=True).encode()#converts blocks to string
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self,chain):#checks to see if the blockchain is valid(check the proof and previous hash)
        previous_block =chain[0] #starts from the first block of the chain
        block_index = 1
        while block_index < len(chain):
            block =chain[block_index]
            if block ['previous_hash'] != self.hash(previous_block):#checks if the previous hash is different for current block
                return False
            previous_proof = previous_block['proof']#compares the proof for parent and child blocks
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':#characters should start with four leading zeros
                return False
            previous_block = block
            block_index += 1
        return True
    
    def add_transactions(self,sender,receiver,amount):
        self.transactions.append({'sender' : sender,
                                  'receiver' : receiver,
                                  'amount' : amount})
        previous_block = self.get_previous_block()#apppends the new trasaction to the new block created
        return previous_block['index'] + 1 #returns the last block created(note that the previous block already has a transaction in it)
    
    def  add_node(self,address):#adds the node containing that address to the set of nodes
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    
        



#part 2: Minning our Blockchain


#Creating A Web App
app = Flask(__name__)

#Creating  A Blockchain
blockchain = Blockchain()       

#Minning a new block
@app.route('/mine_block' , methods=['GET'])   #request
def mine_block():
    previous_block = blockchain.get_previous_block()      #gets the previous block
    previous_proof = previous_block['proof'] #gets the previous proof
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'congratulations you just mined a block!',
                'index': block['index'],
                'timestamp' : block['timestamp'],
                'proof': block['proof'],
                'previous_hash' :block['previous_hash']}
    return jsonify(response), 200


# Get the full Blockchain
@app.route('/get_chain' , methods=['GET'])   #request
def get_chain():
    response = {'chain ': blockchain.get_chain,
                'length': len(blockchain.get_chain)}
    return jsonify(response), 200

# part 3 - Decentralizing our Blockchain    

# Running the App
app.run(host = '0.0.0.0', port = 5000)
