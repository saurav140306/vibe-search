import os
import numpy as np
import pandas as pd
import torch
from transformers import CLIPModel, CLIPProcessor
from PIL import Image
import torch.nn.functional as F

# === Load CLIP model directly from transformers ===
print("Loading CLIP model...")
_model_name = "openai/clip-vit-base-patch32"
_model = CLIPModel.from_pretrained(_model_name)
_processor = CLIPProcessor.from_pretrained(_model_name)
_model.eval()
print("CLIP loaded.")

# === Cache for per-city data ===
_city_cache = {}


def _load_city_data(city: str):
    """Load embeddings + listings for a city. Cached after first load."""
    if city in _city_cache:
        return _city_cache[city]
    
    city_dir = os.path.join('data', city)
    
    if not os.path.isdir(city_dir):
        raise ValueError(f"City '{city}' not found. Expected folder: {city_dir}")
    
    print(f"Loading {city} data...")
    
    embeddings_path = os.path.join(city_dir, 'embeddings.npz')
    listings_path = os.path.join(city_dir, 'listings_clean.csv')
    
    data = np.load(embeddings_path)
    listing_ids = data['listing_ids']
    embeddings = data['embeddings']
    
    df = pd.read_csv(listings_path)
    
    _city_cache[city] = {
        'listing_ids': listing_ids,
        'embeddings': torch.tensor(embeddings),  # convert to torch for cos_sim
        'df': df,
    }
    
    print(f"  Loaded {len(embeddings)} listings for {city}")
    return _city_cache[city]


def search(image: Image.Image, city: str = 'barcelona', top_k: int = 10) -> list:
    """
    Given a PIL Image and a city, return top_k most visually similar listings.
    """
    city_data = _load_city_data(city)
    listing_ids = city_data['listing_ids']
    embeddings = city_data['embeddings']
    df = city_data['df']
    
    # Make sure image is in RGB mode (CLIP requires it)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Direct CLIP encoding using transformers
    with torch.no_grad():
        inputs = _processor(images=image, return_tensors="pt")
        query_embedding = _model.get_image_features(**inputs)[0]
    
    # Normalize both query and stored embeddings (cosine similarity)
    query_norm = F.normalize(query_embedding, dim=0)
    embedding