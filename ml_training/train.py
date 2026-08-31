"""
Trains the Siamese network on CEDAR signature pairs.

Signers are split into train/test groups (not individual images) so
the model is validated on people it has never seen during training —
this is what makes the resulting evaluation numbers meaningful for a
real signature verification system, rather than just memorization.
"""

import torch
from torch.utils.data import DataLoader
import torch.optim as optim

from dataset import get_signer_folders, build_pairs, SignaturePairDataset
from model import SiameseNetwork, ContrastiveLoss

DATASET_DIR = "dataset/CEDAR"
MODEL_OUTPUT_PATH = "../app/ml/signature_model.pth"
EPOCHS = 10
BATCH_SIZE = 16
LEARNING_RATE = 0.0005


def main():
    signer_ids = get_signer_folders(DATASET_DIR)
    print(f"Found {len(signer_ids)} signers.")

    train_signers = signer_ids[:45]
    test_signers = signer_ids[45:]

    train_pairs = build_pairs(DATASET_DIR, train_signers)
    print(f"Training pairs: {len(train_pairs)}")

    train_loader = DataLoader(
        SignaturePairDataset(train_pairs), batch_size=BATCH_SIZE, shuffle=True
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on: {device}")

    model = SiameseNetwork().to(device)
    criterion = ContrastiveLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0.0

        for img1, img2, label in train_loader:
            img1, img2, label = img1.to(device), img2.to(device), label.to(device)

            optimizer.zero_grad()
            embedding1, embedding2 = model(img1, img2)
            loss = criterion(embedding1, embedding2, label)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(train_loader)
        print(f"Epoch {epoch + 1}/{EPOCHS} - Loss: {avg_loss:.4f}")

        # Save after every epoch so we don't lose progress if interrupted
        torch.save(model.state_dict(), MODEL_OUTPUT_PATH)

    print(f"Training complete. Model saved to {MODEL_OUTPUT_PATH}")


if __name__ == "__main__":
    main()