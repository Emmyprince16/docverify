"""
Siamese network for signature verification.

Two identical CNN branches (shared weights, since it's the same
`self.cnn` object used for both images) each embed a signature image
into a 128-dimensional vector. The distance between two embeddings
tells us how similar the signatures are.
"""

import torch.nn as nn
import torch.nn.functional as F


class SiameseNetwork(nn.Module):
    def __init__(self):
        super().__init__()

        self.cnn = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=5, stride=1, padding=2),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),

            nn.Conv2d(32, 64, kernel_size=5, stride=1, padding=2),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),

            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
        )

        # 155 -> 77 -> 38 -> 19 after three 2x2 max-pools
        self.fc = nn.Sequential(
            nn.Linear(128 * 19 * 19, 256),
            nn.ReLU(inplace=True),
            nn.Linear(256, 128),
        )

    def forward_once(self, x):
        x = self.cnn(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return x

    def forward(self, img1, img2):
        embedding1 = self.forward_once(img1)
        embedding2 = self.forward_once(img2)
        return embedding1, embedding2


class ContrastiveLoss(nn.Module):
    """
    label = 1.0 for genuine pairs (should end up close together)
    label = 0.0 for forged pairs (should end up far apart, at least `margin`)
    """
    def __init__(self, margin=2.0):
        super().__init__()
        self.margin = margin

    def forward(self, embedding1, embedding2, label):
        distance = F.pairwise_distance(embedding1, embedding2)
        loss = label * distance.pow(2) + (1 - label) * F.relu(self.margin - distance).pow(2)
        return loss.mean()