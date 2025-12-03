
import torch
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
import numpy as np
from PIL import Image
import json

class SyntheticShapeDataset(Dataset):
    """PyTorch Dataset for synthetic 3D shape images + SDF pairs"""

    def __init__(self, root_dir, split='train', transform=None):
        self.root_dir = Path(root_dir)
        self.split = split
        self.transform = transform

        self.image_dir = self.root_dir / 'images'
        self.sdf_dir = self.root_dir / 'sdfs'

        # Load manifest of all (image, sdf) pairs
        self.pairs = self._load_pairs()

    def _load_pairs(self):
        """Load list of (image_path, sdf_path) pairs"""
        pairs = []
        for image_file in sorted(self.image_dir.glob('*.png')):
            model_id = image_file.stem.rsplit('_', 1)[0]
            view_id = image_file.stem.rsplit('_', 1)[1]

            sdf_file = self.sdf_dir / f"{model_id}_{view_id}.sdf"
            if sdf_file.exists():
                pairs.append((image_file, sdf_file))

        # Split into train/val/test (80/10/10)
        split_idx = int(len(pairs) * 0.8)
        val_idx = int(len(pairs) * 0.9)

        if self.split == 'train':
            return pairs[:split_idx]
        elif self.split == 'val':
            return pairs[split_idx:val_idx]
        else:
            return pairs[val_idx:]

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        image_path, sdf_path = self.pairs[idx]

        # Load image
        image = Image.open(image_path).convert('RGB')
        if self.transform:
            image = self.transform(image)
        image = torch.from_numpy(np.array(image)).permute(2, 0, 1).float() / 255.0

        # Load SDF (64x64x64 float32)
        sdf = np.fromfile(sdf_path, dtype=np.float32).reshape(64, 64, 64)
        sdf = torch.from_numpy(sdf).float()

        return {
            'image': image,
            'sdf': sdf,
            'image_path': str(image_path),
            'sdf_path': str(sdf_path)
        }

def create_data_loaders(root_dir, batch_size=32, num_workers=4):
    """Create train/val/test data loaders"""

    train_dataset = SyntheticShapeDataset(root_dir, split='train')
    val_dataset = SyntheticShapeDataset(root_dir, split='val')
    test_dataset = SyntheticShapeDataset(root_dir, split='test')

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True
    )

    return train_loader, val_loader, test_loader

# Usage:
# train_loader, val_loader, test_loader = create_data_loaders('data/synthetic_shapes')
# for batch in train_loader:
#     images = batch['image']      # (B, 3, 256, 256)
#     sdfs = batch['sdf']          # (B, 64, 64, 64)
#     print(f"Batch: images {images.shape}, sdfs {sdfs.shape}")
