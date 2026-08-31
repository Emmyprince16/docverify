"""
Loads the trained Siamese network and compares a newly uploaded
signature image against a signer's stored reference signature.
"""

import sys
import os
import torch
from PIL import Image
import torchvision.transforms as transforms

# Allow importing the model definition from ml_training
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "ml_training"))
from model import SiameseNetwork

MODEL_PATH = os.path.join(os.path.dirname(__file__), "signature_model.pth")
IMAGE_SIZE = 155

transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
])

_model = None


def load_model():
    """
    Loads the model once and reuses it across requests, instead of
    reloading from disk on every single verification (which would be slow).
    """
    global _model
    if _model is None:
        _model = SiameseNetwork()
        _model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device("cpu")))
        _model.eval()
    return _model


def compare_signatures(reference_path: str, uploaded_path: str, threshold: float = 1.0) -> dict:
    """
    Returns a similarity score and match decision by comparing two
    signature images using the trained Siamese network.

    A LOWER distance means MORE similar. We convert distance into a
    0-1 similarity score for a more intuitive display, where 1.0 means
    identical and 0.0 means very dissimilar.
    """
    model = load_model()

    img1 = transform(Image.open(reference_path).convert("L")).unsqueeze(0)
    img2 = transform(Image.open(uploaded_path).convert("L")).unsqueeze(0)

    with torch.no_grad():
        embedding1, embedding2 = model(img1, img2)
        distance = torch.nn.functional.pairwise_distance(embedding1, embedding2).item()

    # Convert distance to a bounded similarity score for display purposes.
    similarity_score = max(0.0, 1.0 - (distance / (threshold * 2)))
    is_match = distance < threshold

    return {
        "similarity_score": round(similarity_score, 4),
        "match_result": is_match,
        "threshold_used": threshold,
    }