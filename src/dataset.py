import os
from torch.utils.data import Dataset
from PIL import Image
import torchvision.transforms as T

class ImageDataset(Dataset):
    def __init__(self, folder):
        self.files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(('.jpg', '.png'))]
        self.transform = T.Compose([
            T.ToTensor(),
            T.Normalize([0.5], [0.5])
        ])
    
    def __len__(self):
        return len(self.files)
    
    def __getitem__(self, idx):
        img = Image.open(self.files[idx]).convert("RGB")
        return self.transform(img)