from datasets import load_dataset, Image, disable_progress_bar
from PIL import Image as PILImage
import torchvision.transforms as T
import io
import requests
from multiprocessing import cpu_count

# Configuration
SUBSET_FRACTION = 0.1  # 0.1% of full dataset
NUM_PROC = 48
MAX_RETRIES = 3
TIMEOUT = 10

# Load full dataset first
full_dataset = load_dataset(
    "Spawning/PD12M",
    split="train[:1%]",  # Load full train split
)

# Calculate subset size
subset_size = int(len(full_dataset) * SUBSET_FRACTION)
subset_indices = list(range(subset_size))

# Create subset dataset
subset_dataset = full_dataset.select(subset_indices)

# Image processing pipeline remains the same
transform = T.Compose([
    T.Resize(512, interpolation=T.InterpolationMode.BICUBIC),
    T.CenterCrop(512),
    T.RandomHorizontalFlip(p=0.5),
    T.ToTensor(),
    T.Normalize(mean=[0.5]*3, std=[0.5]*3)
])

def download_image(url):
    for _ in range(MAX_RETRIES):
        try:
            response = requests.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            return PILImage.open(io.BytesIO(response.content)).convert("RGB")
        except Exception as e:
            continue
    return None

def preprocess(example):
    img = download_image(example["url"])
    if not img:
        return None
    example["pixel_values"] = transform(img)
    example["text"] = example["caption"][:512]
    return example

# Process subset
processed_dataset = subset_dataset.map(
    preprocess,
    remove_columns=["url", "caption"],
    num_proc=NUM_PROC,
    batched=False,
    load_from_cache_file=False,
    desc=f"Processing {subset_size} images"
)

# Filter failures
processed_dataset = processed_dataset.filter(
    lambda x: x["pixel_values"] is not None,
    num_proc=NUM_PROC
)

# Save processed data
processed_dataset.save_to_disk(
    "pd12m_subset_preprocessed",
    num_proc=NUM_PROC,
    max_shard_size="500MB"
)

print(f"Successfully processed {len(processed_dataset)} images")