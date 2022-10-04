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
from uuid import uuid4    #generates a unique address
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
       
       self.transactions = [] #empties the list of transactions since it is already added to the block(prepares it for a new transaction)
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
    
    def  add_node(self,address):#adds the node containing that address to the set of nodes(this is for concesus)
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    
    def  replace_chain(self): #replaces all chains with the longest chain, concesus protocol
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain) #it is initicialized to the current chain until a new logest chain is found
        for node in network:
            response = requests.get(f'http://{node}/get_chain') #gets the information of the current node in the chain while looping
            if response.status_code == 200:
                length = response.jason()['length']
                chain = response.jason()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain #lenght of the current chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False
        
    



#part 2: Minning our Blockchain


#Creating A Web App
app = Flask(__name__)


#creating and address for the node in port 5000
node_address = str(uuid4()).replace('-', '')

#Creating  A Blockchain (from the blockchain class already created)
blockchain = Blockchain()       

#Minning a new block
@app.route('/mine_block' , methods=['GET'])   #request  (decorator)
def mine_block():
    previous_block = blockchain.get_previous_block()      #gets the previous block
    previous_proof = previous_block['proof'] #gets the previous proof
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transactions( sender = node_address, receiver = 'saida', amount = 10) 
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'congratulations you just mined a block!',
                'index': block['index'],
                'timestamp' : block['timestamp'],
                'proof': block['proof'],
                'previous_hash' :block['previous_hash'],
                'transactions':block['transactions']}
    return jsonify(response), 200

 
# Get the full Blockchain
@app.route('/get_chain' , methods=['GET'])   #request
def get_chain():
    response = {'chain ': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200


#checking if the blockchain is valid
@app.route('/is_valid' , methods=['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid():
        response = {'message' : 'All good the Blockchain is valid!'}
    else:
        response = {'message': 'Victor we have a problem. The Blockchain is not valid'}
    return jsonify(response), 200

#adding a new transaction to the blockchain
@app.route('/add_transaction' , methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender','receiver','amount']
    if not all (key in json for key in transaction_keys):
        return 'some elements of the transaction are missing!', 400
    index = blockchain.add_transactions(json['sender'],json['receiver'],json['amount'])
    response = {'message': f'This transaction would be added to the block {index}'}
    return jsonify(response), 201

# part 3 - Decentralizing our Blockchain   

#connecting new nodes
@app.route('/connect_node' , methods = ['POST']) 
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is  None:
        return "NO NODE!!" ,400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message' : 'All the nodes are now connected.The IDAcoin Blockchain now contains the following nodes:',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201
    

#replacing  chain by the longest chain if needed
@app.route('/replace_chain' , methods=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message' : 'This node had different chains so the chain was replaced by the longest one!',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'All good the chain is the longest one!!',
                    'actual_chain': blockchain.chain}
    
    return jsonify(response), 200

# Running the App
app.run(host = '0.0.0.0', port = 5000 )
 