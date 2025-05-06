// SPDX-License-Identifier: MIT
pragma solidity ^0.8.25;

/**
 * @title ConceptRegistry
 * @dev Manages copyright licenses for AI training datasets via content hashes.
 */
contract ConceptRegistry {
    struct ImageLicense {
        address owner;
        string spdxId;          // e.g., "CC-BY-4.0", "PDM-1.0" (Public Domain)
        uint256 registeredAt;   // Block timestamp
        bool revoked;           // Revocation status
    }

    // Mapping: contentHash (SHA-256) => License
    mapping(bytes32 => ImageLicense) public licenses;
    
    // Events
    event Registered(bytes32 indexed contentHash, address owner, string spdxId);
    event Revoked(bytes32 indexed contentHash, address owner);

    // Register a new image license
    function registerImage(
        bytes32 _contentHash,
        string calldata _spdxId
    ) external {
        require(licenses[_contentHash].owner == address(0), "Already registered");
        
        licenses[_contentHash] = ImageLicense({
            owner: msg.sender,
            spdxId: _spdxId,
            registeredAt: block.timestamp,
            revoked: false
        });
        
        emit Registered(_contentHash, msg.sender, _spdxId);
    }

    // Revoke an existing license (only owner)
    function revokeImage(bytes32 _contentHash) external {
        ImageLicense storage license = licenses[_contentHash];
        require(license.owner == msg.sender, "Not owner");
        require(!license.revoked, "Already revoked");
        
        license.revoked = true;
        emit Revoked(_contentHash, msg.sender);
    }

    // Check if an image is revokable (public domain cannot be revoked)
    function isRevokable(bytes32 _contentHash) public view returns (bool) {
        ImageLicense storage license = licenses[_contentHash];
        return (keccak256(abi.encodePacked(license.spdxId)) != keccak256(abi.encodePacked("PDM-1.0")));
    }
}