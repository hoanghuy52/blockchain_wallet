from flask import Flask, request
from blockchain import Blockchain
from block import Block
import requests, time, json

# Initialize flask application
app =  Flask(__name__)

# Initialize a blockchain object.
blockchain = Blockchain()

@app.route("/new_transaction", methods=['POST'])
def new_transaction():
    data = request.get_json()
    requried_fields = ['author', 'content']
    if not all(k in data for k in requried_fields):
        return "Bad Request - Invalid transaction data", 400
    
    data['timestamp'] = time.time()

    blockchain.add_new_transaction(data)

    return "Success", 201

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data})

@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if not result:
        return "No transactions to mine"
    return "Block #{} is mined.".format(result)

@app.route('/pending_tx')
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)

@app.route('/block/<int:id>/hash')
def get_block_hash(id):
    t_dict = dict(blockchain.chain[id].__dict__)
    t_dict.pop('hash', None)
    return Block.compute_hash_from_dict(t_dict)

if __name__ == '__main__':
    app.run(debug=True)