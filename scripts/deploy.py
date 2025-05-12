from brownie import ConceptRegistry, accounts, network
import pandas as pd
from datasets import Dataset

def bytes32(data: bytes) -> bytes:
    """Ensure bytes are exactly 32 bytes long"""
    return data.ljust(32, b'\0')[:32]

def main():
    # Load dev account
    dev = accounts.load("admin")  # Ensure you've added this account via `brownie accounts`

    # Deploy ConceptRegistry contract
    print("Deploying ConceptRegistry...")
    registry = ConceptRegistry.deploy({'from': dev})
    print(f"ConceptRegistry deployed to: {registry.address}")

    # Load dataset
    print("Loading dataset...")
    dataset = Dataset.load_from_disk("pd12m_with_ownership")
    df = dataset.to_pandas()

    # check what columns we have in our dataframe
    # print(df.columns.tolist())

    # Validate required columns
    if not {'content_hash'}.issubset(df.columns):
        raise ValueError("Dataset must include 'content_hash' column.")

    # Register sample licenses from the dataset
    print("Registering sample licenses...")

    df_cleaned  = df[['pixel_values', 'text', 'owner', 'is_revoked', 'content_hash']].copy()

    for row in df_cleaned.itertuples(index=False):
        if row.owner == "public_domain":
            continue
        else:
            print(f"Registering the license of owner: {row.owner}")
            try:
                content_hash = bytes.fromhex(row.content_hash)
                spdx_id = 'MIT'
                #ensure content_hash is in 32 bytes to match solidity contract definiton
                content_hash_bytes32 = bytes32(content_hash)
                tx = registry.registerImage(content_hash_bytes32, spdx_id, {'from': dev})
                # wait for confirmation of transaction
                tx.wait(1)
                print(f"✔ Registered: {row.content_hash} with SPDX: {spdx_id}")
            except Exception as e:
                print(f"✖ Failed to register: {row.content_hash}, Error: {e}")

    print("🎉 Initial dataset licenses registered successfully!")
