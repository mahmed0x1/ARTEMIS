from training import Trainer
from config import Config
from dataset import ImageDataset
from torch.utils.data import DataLoader

def main():
    # Setup
    dataset = ImageDataset(Config.DATA_DIR)
    dataloader = DataLoader(dataset, batch_size=Config.BATCH_SIZE)
    trainer = Trainer()
    
    # Training loop
    for epoch in range(Config.EPOCHS):
        print(f"Epoch {epoch+1}/{Config.EPOCHS}")
        trainer.train_epoch(dataloader, epoch)

if __name__ == "__main__":
    main()