from ape import accounts, project
import hashlib

def sha256_hex(data: str) -> bytes:
    return bytes.fromhex(hashlib.sha256(data.encode()).hexdigest())

def main():
    dev = accounts.load("dev")
    dev.set_autosign(True)

    print("Deploying ConceptRegistry...")
    registry = project.ConceptRegistry.deploy(sender=dev)
    print(f"Contract deployed to: {registry.address}")

    # Example content to hash
    image_data = "example-image-123"
    content_hash = sha256_hex(image_data)
    spdx_id = "CC-BY-4.0"

    # Register image license
    tx = registry.registerImage(content_hash, spdx_id, sender=dev)
    print("Image license registered.")

    # Read back license info from the mapping
    license = registry.licenses(content_hash)
    print("License Info:")
    print(f" - Owner: {license.owner}")
    print(f" - SPDX ID: {license.spdxId}")
    print(f" - Registered At: {license.registeredAt}")
    print(f" - Revoked: {license.revoked}")
