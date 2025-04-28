from web3 import Web3
from config import Config

class Blockchain:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(Config.POLYGON_RPC))
        self.contract = self._load_contract()
    
    def _load_contract(self):
        with open("./contracts/ConceptRegistry.json") as f:
            abi = json.load(f)["abi"]
        return self.w3.eth.contract(
            address=Config.CONTRACT_ADDRESS,
            abi=abi
        )
    
    def get_policies(self):
        """Fetch active policies from blockchain"""
        return self.contract.functions.getActivePolicies().call()
    
    def submit_proof(self, proof_data):
        """Submit proof to blockchain"""
        tx = self.contract.functions.submitProof(proof_data).buildTransaction({
            'chainId': 80001,
            'gas': 2000000,
            'gasPrice': self.w3.toWei('30', 'gwei'),
            'nonce': self.w3.eth.getTransactionCount(self.w3.eth.account.from_key(Config.PRIVATE_KEY).address),
        })
        signed_tx = self.w3.eth.account.sign_transaction(tx, Config.PRIVATE_KEY)
        return self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)