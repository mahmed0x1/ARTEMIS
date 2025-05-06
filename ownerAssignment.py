import pandas as pd
import numpy as np
from datasets import load_from_disk

from datasets import load_from_disk
try:
    dataset = load_from_disk("pd12m_subset_preprocessed")
except Exception as e:
    print(f"Corrupted shards: {e}")

# Load preprocessed dataset
dataset = load_from_disk("pd12m_subset_preprocessed")
df = dataset.to_pandas()

# Initialize metadata
df["owner"] = "public_domain"
df["is_revoked"] = False
df["content_hash"] = ""

# List of owners and their min/max images
owners = ["alice", "bob", "chelsea", "dylan", "elana"]
min_images = 100
max_images = 200

# Track available public domain indices
public_domain_indices = df[df["owner"] == "public_domain"].index.tolist()

for owner in owners:
    # Randomly choose number of images for this owner
    n_images = np.random.randint(min_images, max_images + 1)
    
    # Ensure we don't exceed available images
    n_images = min(n_images, len(public_domain_indices))
    if n_images == 0:
        break  # No more images to assign
    
    # Randomly select indices without replacement
    selected_indices = np.random.choice(public_domain_indices, n_images, replace=False)
    
    # Update ownership
    df.loc[selected_indices, "owner"] = owner
    
    # Remove assigned indices from available pool
    public_domain_indices = list(set(public_domain_indices) - set(selected_indices))

# Compute content hashes (using all 48 CPUs)
def compute_hash(row):
    img_bytes = row["pixel_values"].numpy().tobytes()
    return hashlib.sha256(img_bytes).hexdigest()

df["content_hash"] = df.apply(compute_hash, axis=1)

# Save back to disk
dataset_with_metadata = Dataset.from_pandas(df)
dataset_with_metadata.save_to_disk(
    "pd12m_with_ownership",
    num_proc=48,
    max_shard_size="500MB"
)

# Print final distribution
print("Final ownership distribution:")
print(df["owner"].value_counts())