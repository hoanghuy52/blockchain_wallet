from flask import Flask, render_template, request, session, escape, url_for, redirect
import requests, json
from signature import Signature
app = Flask(__name__)
app.debug = True
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000/"
posts = []

def fetch_posts():
    """
    Function to fetch the chain from a blockchain node, parse the
    data, and store it locally.
    """
    get_chain_address = "{}chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        for block in chain["chain"]:
            for tx in block["transactions"]:
                tx["index"] = block["index"]
                tx["hash"] = block["previous_hash"]
                content.append(tx)

        global posts
        posts = sorted(content,
                       key=lambda k: k['timestamp'],
                       reverse=True)

@app.route('/')
def index():
    if 'private_key' in session:
        return 'Logged in as %s' % escape(session['private_key'])
    return 'You are not logged in'

@app.route("/login", methods=['POST'])
def login():
    data = request.get_json()
    required_fields = ['private_key']

    if not all(k in data for k in required_fields):
        return "Bad Request", 400
    try:
        Signature.get_public_key(data['private_key'])
    except Exception as e:
        return "Private key is not valid"
    session['private_key'] = data['private_key']
    return 'Success'

@app.route("/key")
def key():
    return session['private_key']

@app.route("/posts")
def posts():
    return json.dumps(posts)

@app.route("/amounts")
def get_money():
    return {
        "amount": get_amount()
    }


def get_amount():
    fetch_posts()
    init_amount = 1000
    for post in posts:
        if post['sender'] == Signature.get_public_key(session['private_key']):
            init_amount -= post['amount']
        if post['receiver'] == Signature.get_public_key(session['private_key']):
            init_amount += post['amount']
    return init_amount

@app.route("/transaction", methods=['POST'])
def create_transaction():
    if 'private_key' not in session:
        return 'You are not logged in'
    data = request.get_json()
    required_fields = ['receiver', 'amount']
    if not all(k in data for k in required_fields):
        return "Bad Request", 400
    init_amount = get_amount()
    if init_amount >= data['amount']:
        trans = {
            'sender': Signature.get_public_key(session['private_key']),
            'receiver': data['receiver'],
            'amount': data['amount']
        }
        signature = Signature.sign(session['private_key'], json.dumps(trans, sort_keys=True))
        trans['signature'] = signature
        headers = {'Content-Type': "application/json"}
        url = "{}new_transaction".format(CONNECTED_NODE_ADDRESS)
        response = requests.post(url, data=json.dumps(trans), headers=headers)
        if response.ok:
            return 'Success'
        else:
            return response.content
    return 'Not Enough Money'



if __name__ == '__main__':
    fetch_posts()
    app.run()