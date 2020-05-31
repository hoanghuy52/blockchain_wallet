from hashlib import sha256
import json

class Block:
    def __init__(self, index: int, transactions: list, timestamp : int, previous_hash: str):
        """
        Constructor for the `Block` class.
        :param index: Unique ID of the block.
        :param transactions: List of transactions.
        :param timestamp: Time of generation of the block.
        :param previous_hash: Hash of the previous block in the chain which this block is part of. 
        """
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.hash = ""
        self.nonce = 0
    
    def compute_hash(self) -> str:
        """
        Returns the hash of the block instance by first converting it
        into JSON string.
        """
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()

# t = {"a" : "b"}

# b = Block(1, [t], 1590910438)
# print(b.__dict__)
# print(b.compute_hash())