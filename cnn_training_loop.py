
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from pathlib import Path
import json
from datetime import datetime

class CNNTrainer:
    """Training loop for CNN SDF predictor"""

    def __init__(self, model, train_loader, val_loader, device='cuda'):
        self.model = model.to(device)
        self.device = device
        self.train_loader = train_loader
        self.val_loader = val_loader

        # Loss functions
        self.l1_loss = nn.L1Loss()
        self.mse_loss = nn.MSELoss()

        # Optimizer
        self.optimizer = optim.Adam(
            model.parameters(),
            lr=0.0001,
            betas=(0.9, 0.999),
            weight_decay=0.0001
        )

        # Learning rate scheduler
        self.scheduler = optim.lr_scheduler.CosineAnnealingLR(
            self.optimizer,
            T_max=100,
            eta_min=0.00001
        )

        self.training_history = {
            'loss': [],
            'val_loss': [],
            'epochs': []
        }

    def compute_loss(self, predicted_sdf, gt_sdf):
        """Compute multi-component loss"""
        # Main L1 loss
        l1 = self.l1_loss(predicted_sdf, gt_sdf)

        # L2 regularization (weight decay handled by optimizer)
        l2 = 0.0
        for param in self.model.parameters():
            l2 += torch.norm(param)

        # Boundary smoothness (gradient magnitude)
        sdf_grad = torch.abs(torch.gradient(predicted_sdf, dim=(2, 3, 4))).mean()

        total_loss = l1 + 0.0001 * l2 + 0.1 * sdf_grad

        return total_loss, l1.item()

    def train_epoch(self, epoch):
        """Train for one epoch"""
        self.model.train()
        total_loss = 0.0
        total_samples = 0

        for batch_idx, batch in enumerate(self.train_loader):
            images = batch['image'].to(self.device)
            gt_sdf = batch['sdf'].to(self.device)

            # Forward pass
            predicted_sdf = self.model(images)

            # Compute loss
            loss, l1_loss_val = self.compute_loss(predicted_sdf, gt_sdf)

            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
            self.optimizer.step()

            total_loss += loss.item() * images.size(0)
            total_samples += images.size(0)

            if (batch_idx + 1) % 10 == 0:
                avg_loss = total_loss / total_samples
                print(f"Epoch {epoch} [{batch_idx + 1}/{len(self.train_loader)}] Loss: {avg_loss:.6f}")

        avg_loss = total_loss / total_samples
        self.training_history['loss'].append(avg_loss)
        self.training_history['epochs'].append(epoch)

        return avg_loss

    def validate(self, epoch):
        """Validate on validation set"""
        self.model.eval()
        total_loss = 0.0
        total_samples = 0

        with torch.no_grad():
            for batch in self.val_loader:
                images = batch['image'].to(self.device)
                gt_sdf = batch['sdf'].to(self.device)

                predicted_sdf = self.model(images)
                loss, _ = self.compute_loss(predicted_sdf, gt_sdf)

                total_loss += loss.item() * images.size(0)
                total_samples += images.size(0)

        avg_val_loss = total_loss / total_samples
        self.training_history['val_loss'].append(avg_val_loss)

        return avg_val_loss

    def train(self, num_epochs=100, save_interval=10):
        """Main training loop"""
        print(f"Starting training for {num_epochs} epochs on {self.device}")

        best_val_loss = float('inf')
        patience_counter = 0

        for epoch in range(1, num_epochs + 1):
            # Train
            train_loss = self.train_epoch(epoch)

            # Validate
            val_loss = self.validate(epoch)

            # Learning rate scheduling
            self.scheduler.step()

            print(f"Epoch {epoch}: Train Loss={train_loss:.6f}, Val Loss={val_loss:.6f}")

            # Save checkpoint
            if epoch % save_interval == 0:
                self.save_checkpoint(epoch)

            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                self.save_checkpoint(epoch, is_best=True)
            else:
                patience_counter += 1

            if patience_counter >= 20:
                print(f"Early stopping at epoch {epoch}")
                break

        return self.training_history

    def save_checkpoint(self, epoch, is_best=False):
        """Save model checkpoint"""
        checkpoint = {
            'epoch': epoch,
            'model_state': self.model.state_dict(),
            'optimizer_state': self.optimizer.state_dict(),
            'training_history': self.training_history
        }

        filename = f"checkpoint_epoch_{epoch}.pt"
        if is_best:
            filename = "checkpoint_best.pt"

        torch.save(checkpoint, filename)
        print(f"Saved checkpoint: {filename}")

# Usage:
# model = ResNet50SDFPredictor()
# trainer = CNNTrainer(model, train_loader, val_loader)
# history = trainer.train(num_epochs=100)
