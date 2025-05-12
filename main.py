from ArtemisOracle import LicenseOracle
from datasets import load_from_disk

# This code tests if we can access the blockchain licenses
def main():
    # Initialize oracle with contract address
    license_oracle = LicenseOracle("0xDdfAF53F524f15F2779Aa5Ad89a410B819135Aa3")
    
    # Load your dataset
    dataset = load_from_disk("pd12m_with_ownership")
    
    # Find a registered image (first one with non-public domain owner)
    registered_sample = None
    for sample in dataset:
        if sample['owner'] != 'public_domain':
            registered_sample = sample
            break
    
    if not registered_sample:
        print("No registered images found in dataset!")
        return
    
    print(f"Testing with image owned by: {registered_sample['owner']}")
    print(f"Image text: {registered_sample['text']}")
    
    # Check license status
    content_hash = registered_sample['content_hash']
    status = license_oracle.get_license_status(content_hash)
    
    print("\nLicense Status:")
    print(f"Content Hash: {content_hash}")
    print(f"Exists: {status['exists']}")
    print(f"Valid: {status['valid']}")
    print(f"Owner: {status['owner']}")
    print(f"License: {status['license']}")
    print(f"Registered At: {status['registered_at']}")
    print(f"Revoked: {status['revoked']}")
    print(f"Revokable: {status['revokable']}")


if __name__ == "__main__":
    main()