import json
import requests
import time
from flask import Flask, request

from block import Block
from blockchain import Blockchain
from signature import Signature

# Initialize flask application
app = Flask(__name__)

# Initialize a blockchain object.
blockchain = Blockchain()

# Contains the host addresses of other participating members of the network
peers = set()

# Private key and Public key
private_key = None
public_key = None


# Endpoint to add new peers to the network
@app.route('/register_node', methods=['POST'])
def register_new_peers():
    # The host address to the peer node 
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    # Return exist peers
    d_peers = json.loads(get_peers())

    # Add the node to the peer list
    peers.add(node_address)

    # Return the blockchain to the newly registered node so that it can sync
    d_chains = json.loads(get_chain())
    return {**d_chains, **d_peers}


@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
    """
    Internally calls the `register_node` endpoint to
    register current node with the remote node specified in the
    request, and sync the blockchain as well with the remote node.
    """
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    data = {"node_address": request.host_url}
    headers = {'Content-Type': "application/json"}

    # Make a request to register with remote node and obtain information
    response = requests.post(node_address + "/register_node",
                             data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        global blockchain
        global peers
        # update chain and the peers
        chain_dump = response.json()['chain']
        blockchain = create_chain_from_dump(chain_dump)
        peers.update(response.json()['peers'])
        return "Registration successful", 200
    else:
        # if something goes wrong, pass it on to the API response
        return response.content, response.status_code


def create_chain_from_dump(chain_dump):
    global blockchain
    blockchain = Blockchain()
    for idx, block_data in enumerate(chain_dump):
        block = Block(block_data["index"],
                      block_data["transactions"],
                      block_data["timestamp"],
                      block_data["previous_hash"])
        proof = block_data['hash']
        if idx > 0:
            added = blockchain.add_block(block, proof)
            if not added:
                raise Exception("The chain dump is tampered!!")
        else:  # the block is a genesis block, no verification needed
            blockchain.chain.append(block)
    return blockchain


def consensus():
    """
    Our simple consensus algorithm. If a longer valid chain is
    found, our chain is replaced with it.
    """
    global blockchain

    longest_chain = None
    current_len = len(blockchain.chain)

    for node in peers:
        response = requests.get('{}/chain'.format(node))
        length = response.json()['length']
        chain = response.json()['chain']
        if length > current_len and blockchain.check_chain_validity(chain):
            # Longer valid chain found!
            current_len = length
            longest_chain = chain

    if longest_chain:
        blockchain = longest_chain
        return True

    return False


# endpoint to add a block mined by someone else to
# the node's chain. The node first verifies the block
# and then adds it to the chain.
@app.route('/add_block', methods=['POST'])
def verify_and_add_block():
    block_data = request.get_json()
    block = Block(block_data["index"],
                  block_data["transactions"],
                  block_data["timestamp"],
                  block_data["previous_hash"])

    proof = block_data['hash']
    added = blockchain.add_block(block, proof)

    if not added:
        return "The block was discarded by the node", 400

    return "Block added to the chain", 201


def announce_new_block(block):
    """
    A function to announce to the network once a block has been mined.
    Other blocks can simply verify the proof of work and add it to their
    respective chains.
    """
    headers = {'Content-Type': "application/json"}
    for peer in peers:
        url = "{}add_block".format(peer)
        requests.post(url, data=json.dumps(block.__dict__, sort_keys=True), headers=headers)


def announce_new_transaction(transaction):
    """
    A function to announce to the network once a transaction is come.
    """
    headers = {'Content-Type': "application/json"}

    for peer in peers:
        url = "{}new_transaction".format(peer)
        requests.post(url, data=json.dumps(transaction), headers=headers)


@app.route("/new_transaction", methods=['POST'])
def new_transaction():
    data = request.get_json()
    print(data)
    required_fields = ['author', 'content', 'signature']
    if not all(k in data for k in required_fields):
        return "Bad Request - Invalid transaction data", 400

    announce_new_transaction(data)

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
    else:
        # Making sure we have the longest chain before announcing to the network
        chain_length = len(blockchain.chain)
        consensus()
        if chain_length == len(blockchain.chain):
            # announce the recently mined block to the network
            announce_new_block(blockchain.last_block)
        return "Block #{} is mined.".format(blockchain.last_block.index)


@app.route('/pending_tx')
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)


@app.route('/block/<int:id>/hash')
def get_block_hash(id):
    t_dict = dict(blockchain.chain[id].__dict__)
    t_dict.pop('hash', None)
    return Block.compute_hash_from_dict(t_dict)


@app.route('/peers')
def get_peers():
    return json.dumps({
        "peers": list(peers)
    })


@app.route('/generator')
def generate_key():
    _private_key, _public_key = Signature.generate()
    return json.dumps({
        "private_key": _private_key,
        "public_key": _public_key,
    })


@app.route('/create_account')
def create_account():
    _private_key, _public_key = Signature.generate()
    with open('private.key', 'w') as f:
        f.write(_private_key)
        f.close()
    return json.dumps({
        "private_key": _private_key,
        "public_key": _public_key,
    })


if __name__ == '__main__':
    app.run(debug=True)
