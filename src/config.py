import os

class Config:
    # Blockchain
    POLYGON_RPC = os.getenv("POLYGON_RPC", "https://rpc-mumbai.maticvigil.com")
    CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "")
    PRIVATE_KEY = os.getenv("PRIVATE_KEY", "")
    
    # Model
    MODEL_NAME = "stabilityai/stable-diffusion-2-base"
    
    # Training
    BATCH_SIZE = 4
    LEARNING_RATE = 1e-5
    EPOCHS = 50
    DATA_DIR = "./data"