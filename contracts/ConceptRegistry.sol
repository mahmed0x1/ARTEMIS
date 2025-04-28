// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title ARTEMIS Concept Registry
 * @dev Manages copyright policies and training compliance proofs for diffusion models
 */
contract ConceptRegistry {
    // Struct to store policy information
    struct Policy {
        address owner;
        string conceptCID; // IPFS hash of concept description
        uint256 timestamp;
        bool isActive;
    }

    // Struct to store model training proofs
    struct TrainingProof {
        bytes32 proofHash;
        uint256 epoch;
        uint256 timestamp;
    }

    // State variables
    mapping(bytes32 => Policy) public policies;
    mapping(address => TrainingProof[]) public modelProofs;
    address public admin;

    // Events
    event PolicyRegistered(bytes32 indexed policyId, address indexed owner, string conceptCID);
    event PolicyDeactivated(bytes32 indexed policyId);
    event ProofSubmitted(address indexed modelAddress, uint256 epoch, bytes32 proofHash);

    // Modifier for admin-only functions
    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can call this");
        _;
    }

    constructor() {
        admin = msg.sender;
    }

    /**
     * @dev Registers a new copyright policy
     * @param _conceptCID IPFS hash of the concept description
     * @return policyId The generated policy ID
     */
    function registerPolicy(string memory _conceptCID) external returns (bytes32) {
        bytes32 policyId = keccak256(abi.encodePacked(_conceptCID, block.timestamp, msg.sender));
        
        policies[policyId] = Policy({
            owner: msg.sender,
            conceptCID: _conceptCID,
            timestamp: block.timestamp,
            isActive: true
        });

        emit PolicyRegistered(policyId, msg.sender, _conceptCID);
        return policyId;
    }

    /**
     * @dev Deactivates a policy
     * @param _policyId The policy ID to deactivate
     */
    function deactivatePolicy(bytes32 _policyId) external onlyAdmin {
        require(policies[_policyId].isActive, "Policy already inactive");
        policies[_policyId].isActive = false;
        emit PolicyDeactivated(_policyId);
    }

    /**
     * @dev Submits a training proof for a model
     * @param _proofHash Hash of the zk-SNARK proof
     * @param _epoch The training epoch number
     */
    function submitProof(bytes32 _proofHash, uint256 _epoch) external {
        modelProofs[msg.sender].push(TrainingProof({
            proofHash: _proofHash,
            epoch: _epoch,
            timestamp: block.timestamp
        }));

        emit ProofSubmitted(msg.sender, _epoch, _proofHash);
    }

    /**
     * @dev Gets all active policies
     * @return activePolicies Array of active policy IDs
     */
    function getActivePolicies() external view returns (bytes32[] memory) {
        bytes32[] memory activePolicies = new bytes32[](getActivePolicyCount());
        uint256 counter = 0;
        
        // This is inefficient for large numbers of policies - consider using
        // an indexed approach in production
        bytes32[] memory allPolicyIds = getAllPolicyIds();
        for (uint256 i = 0; i < allPolicyIds.length; i++) {
            if (policies[allPolicyIds[i]].isActive) {
                activePolicies[counter] = allPolicyIds[i];
                counter++;
            }
        }
        
        return activePolicies;
    }

    // Helper function to get all policy IDs (simplified - in production use events)
    function getAllPolicyIds() internal pure returns (bytes32[] memory) {
        // In a real implementation, you would track policy IDs when they're created
        // This is a placeholder that assumes you'll modify it based on your needs
        bytes32[] memory dummy = new bytes32[](0);
        return dummy;
    }

    // Helper function to count active policies
    function getActivePolicyCount() internal view returns (uint256) {
        // Similarly, this should be replaced with actual tracking
        return 0;
    }
}