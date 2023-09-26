import datetime
import hashlib
import json
from flask import Flask, jsonify, request

class Blockchain:

    def __init__(self):
        self.chain = []
        # genesis block 
        self.create_block(proof=1, prev_hash='0', hash_operation='0')

    def create_block(self, proof, prev_hash, hash_operation, data=None):
        # Tambahkan 'data' ke blok
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'prev_hash': prev_hash,
            'hash_operation': hash_operation,
            'block_hash': self.hash({
                'index': len(self.chain) + 1,
                'timestamp': str(datetime.datetime.now()),
                'proof': proof,
                'prev_hash': prev_hash,
                'hash_operation': hash_operation,
                'data': data  # Tambahkan 'data' ke blok
            })
        }
        self.chain.append(block)
        return block

    def get_prev_block(self):
        return self.chain[-1]

    def proof_of_work(self, prev_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - prev_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof, hash_operation

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        hash_operation = hashlib.sha256(encoded_block).hexdigest()
        return hash_operation

    def is_chain_valid(self, chain):
        prev_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['prev_hash'] != self.hash(prev_block):
                return False
            prev_proof = prev_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - prev_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            prev_block = block
            block_index += 1
        return True

app = Flask(__name__)

blockchain = Blockchain()

@app.route('/mine_block', methods=['GET'])
def mine_block():
    prev_block = blockchain.get_prev_block()
    prev_proof = prev_block['proof']
    proof, hash_operation = blockchain.proof_of_work(prev_proof)
    prev_hash = blockchain.hash(prev_block)
    block = blockchain.create_block(proof, prev_hash, hash_operation)
    response = {
        'message': 'Selamat anda berhasil memiliki block',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'prev_hash': block['prev_hash'],
        'hash_operation': block['hash_operation'],
        'block_hash': block['block_hash']
    }
    return jsonify(response), 200

@app.route('/create', methods=['POST'])
def create_block():
    data = request.form

    prev_block = blockchain.get_prev_block()
    prev_proof = prev_block['proof']
    proof, proof_of_work = blockchain.proof_of_work(prev_proof)
    prev_hash = blockchain.hash(prev_block)
    created_block = blockchain.create_block(proof, prev_hash, proof_of_work, data['data'])
    response = {
        'message': 'Blockchain is successfully created',
        'created_block': created_block
    }
    return jsonify(response), 200

@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {
        'length': len(blockchain.chain),
        'chain': blockchain.chain
    }
    return jsonify(response), 200

@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'Semua blockchain sudah valid'}
    else:
        response = {'message': 'Maaf, blockchain anda tidak valid'}
    return jsonify(response), 200

app.run(host='0.0.0.0', port=5001)
