from brownie import Contract, network
import hashlib
from datetime import datetime
from typing import Tuple, Optional, Dict, Any, List, Union
import json
import warnings
from pathlib import Path
from web3.exceptions import ContractLogicError

class LicenseOracle:
    def __init__(self, registry_address: str):
        """
        Initialize the oracle with contract address.
        
        Args:
            registry_address: Address of the deployed ConceptRegistry contract
        """
        if not network.is_connected():
            network.connect("amoy")
        
        self.registry = self._load_contract(registry_address)
        self._validate_registry()

    def _load_contract(self, address: str) -> Contract:
        """Load and validate the contract ABI"""
        abi_path = Path("build/contracts/ConceptRegistry.json")
        if not abi_path.exists():
            raise FileNotFoundError(
                "Contract ABI not found. Run 'brownie compile' first."
            )
        
        with abi_path.open() as f:
            abi = json.load(f)["abi"]
    
        return Contract.from_abi("ConceptRegistry", address, abi)

    def _validate_registry(self):
        """Verify contract has all required functions with correct signatures"""
        required_functions = {
            'licenses': {'inputs': ['bytes32'], 'outputs': ['address', 'string', 'uint256', 'bool']},
            'registerImage': {'inputs': ['bytes32', 'string'], 'outputs': []},
            'revokeImage': {'inputs': ['bytes32'], 'outputs': []},
            'isRevokable': {'inputs': ['bytes32'], 'outputs': ['bool']}
        }
        
        contract_abi = {fn['name']: fn for fn in self.registry.abi if fn['type'] == 'function'}
        
        for fn_name, fn_spec in required_functions.items():
            if fn_name not in contract_abi:
                raise ValueError(f"Contract missing required function: {fn_name}")
            
            # Validate input/output types
            abi_fn = contract_abi[fn_name]
            if [i['type'] for i in abi_fn['inputs']] != fn_spec['inputs']:
                raise ValueError(f"Function {fn_name} has incorrect input parameters")
            if [o['type'] for o in abi_fn['outputs']] != fn_spec['outputs']:
                raise ValueError(f"Function {fn_name} has incorrect return types")

    def _normalize_hash_input(self, content_hash: Union[bytes, str]) -> bytes:
        """
        Normalize hash input to 32-byte format
        
        Args:
            content_hash: Either bytes or string (with or without 0x prefix)
            
        Returns:
            bytes: 32-byte hash
        """
        if isinstance(content_hash, str):
            if content_hash.startswith('0x'):
                content_hash = bytes.fromhex(content_hash[2:])
            else:
                content_hash = bytes.fromhex(content_hash)
        
        if len(content_hash) != 32:
            raise ValueError("Content hash must be 32 bytes")
            
        return content_hash

    def hash_image(self, image_data: bytes) -> bytes:
        """
        Generate SHA-256 hash of image data as bytes (32 bytes)
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            bytes: 32-byte hash
        """
        return hashlib.sha256(image_data).digest()

    def hash_to_bytes32(self, content_hash: Union[bytes, str]) -> str:
        """
        Convert hash to 0x-prefixed hex string for contract interaction
        
        Args:
            content_hash: Either bytes or string (with or without 0x prefix)
            
        Returns:
            str: 0x-prefixed hex string
        """
        content_hash = self._normalize_hash_input(content_hash)
        return "0x" + content_hash.hex()
    
    def get_license(self, content_hash: Union[bytes, str]) -> Tuple[Optional[str], Optional[str], Optional[int], bool]:
        """
        Get license info from blockchain
        
        Args:
            content_hash: Either bytes or string (with or without 0x prefix)
                
        Returns:
            tuple: (owner_address, spdx_id, registered_timestamp, is_revoked)
        """
        try:
            bytes32_hash = self.hash_to_bytes32(content_hash)
            result = self.registry.licenses(bytes32_hash)
            
            # Handle empty registration
            if result[0] == "0x0000000000000000000000000000000000000000":
                return (None, None, None, False)
                
            return result
            
        except ContractLogicError as e:
            if "execution reverted" in str(e):
                return (None, None, None, False)
            raise
            
        except Exception as e:
            warnings.warn(f"License check failed: {str(e)}")
            return (None, None, None, False)
    
    def is_licensed(self, content_hash: Union[bytes, str]) -> bool:
        """Check if image has a valid, non-revoked license"""
        owner, _, _, revoked = self.get_license(content_hash)
        return owner is not None and not revoked

    def is_revokable(self, content_hash: Union[bytes, str]) -> bool:
        """Check if license can be revoked (not public domain)"""
        try:
            bytes32_hash = self.hash_to_bytes32(content_hash)
            return self.registry.isRevokable(bytes32_hash)
        except Exception as e:
            warnings.warn(f"Revokable check failed: {str(e)}")
            return False

    def get_license_status(self, content_hash: Union[bytes, str]) -> Dict[str, Any]:
        """
        Get comprehensive license information
        
        Returns:
            dict: {
                'exists': bool,
                'valid': bool,
                'owner': str,
                'license': str,
                'registered_at': str (ISO format),
                'revoked': bool,
                'revokable': bool
            }
        """
        owner, spdx_id, timestamp, revoked = self.get_license(content_hash)
        
        return {
            'exists': owner is not None,
            'valid': owner is not None and not revoked,
            'owner': owner,
            'license': spdx_id,
            'registered_at': datetime.fromtimestamp(timestamp).isoformat() if timestamp else None,
            'revoked': revoked,
            'revokable': self.is_revokable(content_hash) if owner is not None else False
        }

    def batch_check_licenses(self, content_hashes: List[Union[bytes, str]]) -> Dict[str, Dict[str, Any]]:
        """Check license status for multiple images"""
        return {self.hash_to_bytes32(ch): self.get_license_status(ch) for ch in content_hashes}

    @staticmethod
    def image_file_to_hash(file_path: str) -> bytes:
        """Generate hash directly from image file"""
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).digest()