"""
Builds genuine/forged signature pairs for Siamese network training.

Pairs are split by SIGNER, not by individual image — this ensures the
model is evaluated on signers it has never seen during training. This
is the correct way to test a signature verification system: in the
real world it must generalize to new people, not just memorize the
55 signers in this dataset.
"""

import os
import random
from PIL import Image
import torch
from torch.utils.data import Dataset
import torchvision.transforms as transforms

IMAGE_SIZE = 155  # standard size used in signature verification literature

transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
])


def get_signer_folders(dataset_dir):
    return sorted(
        [f for f in os.listdir(dataset_dir) if os.path.isdir(os.path.join(dataset_dir, f))],
        key=lambda x: int(x)
    )


def build_pairs(dataset_dir, signer_ids):
    """
    For each signer, creates:
    - genuine-genuine pairs (label 1.0, should be judged similar)
    - genuine-forged pairs (label 0.0, should be judged dissimilar)
    """
    pairs = []

    for signer_id in signer_ids:
        signer_path = os.path.join(dataset_dir, signer_id)
        originals = sorted([f for f in os.listdir(signer_path) if f.startswith("original")])
        forgeries = sorted([f for f in os.listdir(signer_path) if f.startswith("forgeries")])

        original_paths = [os.path.join(signer_path, f) for f in originals]
        forged_paths = [os.path.join(signer_path, f) for f in forgeries]

        for i in range(len(original_paths)):
            for j in range(i + 1, len(original_paths)):
                pairs.append((original_paths[i], original_paths[j], 1.0))

        for orig in original_paths:
            for forged in random.sample(forged_paths, min(4, len(forged_paths))):
                pairs.append((orig, forged, 0.0))

    random.shuffle(pairs)
    return pairs


class SignaturePairDataset(Dataset):
    def __init__(self, pairs):
        self.pairs = pairs

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        img1_path, img2_path, label = self.pairs[idx]

        img1 = transform(Image.open(img1_path).convert("L"))
        img2 = transform(Image.open(img2_path).convert("L"))

        return img1, img2, torch.tensor(label, dtype=torch.float32)