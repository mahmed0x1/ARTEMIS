import numpy as np
import hashlib
from tqdm.auto import tqdm
from datasets import load_from_disk, Dataset, disable_progress_bar, Features, Array3D, Value
import logging
import psutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_memory_usage():
    mem = psutil.virtual_memory()
    logger.info(f"Memory used: {mem.used / 1024**3:.2f}GB / {mem.total / 1024**3:.2f}GB")

# Disable datasets internal progress bars
disable_progress_bar()

try:
    logger.info("Loading dataset...")
    dataset = load_from_disk("pd12m_subset_preprocessed", keep_in_memory=False)
except Exception as e:
    logger.error(f"Loading failed: {str(e)}")
    raise

logger.info("Converting to pandas DataFrame...")
log_memory_usage()
df = dataset.to_pandas()

# Initialize metadata
logger.info("Initializing metadata columns...")
df["owner"] = "public_domain"
df["is_revoked"] = False
df["content_hash"] = ""

owners = ["alice", "bob", "chelsea",]
min_images, max_images = 2, 3

public_domain_indices = df[df["owner"] == "public_domain"].index.tolist()

# Owner assignment with progress
logger.info("Assigning owners...")
with tqdm(total=len(owners), desc="Owners processed") as pbar:
    for owner in owners:
        log_memory_usage()
        
        # Calculate number of images to assign
        n_images = np.random.randint(min_images, max_images + 1)
        n_images = min(n_images, len(public_domain_indices))
        if n_images == 0:
            logger.warning("No more public domain images available")
            break
            
        # Select indices
        selected_indices = np.random.choice(public_domain_indices, n_images, replace=False)
        df.loc[selected_indices, "owner"] = owner
        
        # Update available indices
        public_domain_indices = list(set(public_domain_indices) - set(selected_indices))
        pbar.update(1)
        pbar.set_postfix({
            "remaining": len(public_domain_indices),
            "current_owner": owner
        })

# Hashing with chunked processing
def compute_hash_chunk(chunk):
    return [hashlib.sha256(x.tobytes()).hexdigest() for x in chunk]

logger.info("Computing content hashes...")
chunk_size = 1000
total_rows = len(df)
hash_values = []

with tqdm(total=total_rows, desc="Hashing progress") as pbar:
    for start in range(0, total_rows, chunk_size):
        end = min(start + chunk_size, total_rows)
        chunk = df["pixel_values"].iloc[start:end]
        hash_values.extend(compute_hash_chunk(chunk))
        pbar.update(len(chunk))
        log_memory_usage()

df["content_hash"] = hash_values
df = df[["pixel_values", "text", "owner", "is_revoked", "content_hash"]]

# Verify columns
required_columns = {"pixel_values", "text", "owner", "is_revoked", "content_hash"}
missing = required_columns - set(df.columns)
if missing:
    raise ValueError(f"Missing columns: {missing}")

# Convert back to Dataset with memory monitoring
logger.info("Creating final dataset...")
log_memory_usage()

features = Features({
    "pixel_values": Array3D(dtype="float32", shape=(3, 512, 512)),
    "text": Value("string"),
    "owner": Value("string"),
    "is_revoked": Value("bool"),
    "content_hash": Value("string")
})

logger.info("Building dataset with metadata...")
dataset_with_metadata = Dataset.from_pandas(df, features=Features(features))

# Save without multiprocessing
logger.info("Saving dataset...")

dataset_with_metadata.save_to_disk(
    "pd12m_with_ownership",
    num_proc=1,  # ← Changed to single process
    max_shard_size="500MB"
)

logger.info("Final ownership distribution:")
print(df["owner"].value_counts())
