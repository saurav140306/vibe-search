import os
import numpy as np
import pandas as pd
import torch
from transformers import CLIPModel, CLIPImageProcessor
from PIL import Image
import torch.nn.functional as F

# === Load CLIP model directly from transformers ===
print("Loading CLIP model...")
_model_name = "openai/clip-vit-base-patch32"
_model = CLIPModel.from_pretrained(_model_name)
_processor = CLIPImageProcessor.from_pretrained(_model_name)
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
        'embeddings': torch.tensor(embeddings, dtype=torch.float32),
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
    
    # Direct CLIP encoding using transformers (image-only processor)
    with torch.no_grad():
        inputs = _processor(images=image, return_tensors="pt")
        pixel_values = inputs['pixel_values'].to(torch.float32)
        query_embedding = _model.get_image_features(pixel_values=pixel_values)[0]
    
    # Normalize both query and stored embeddings (cosine similarity)
    query_norm = F.normalize(query_embedding, dim=0)
    embeddings_norm = F.normalize(embeddings, dim=1)
    
    scores = (embeddings_norm @ query_norm).numpy()
    
    top_indices = np.argsort(scores)[::-1][:top_k]
    
    results = []
    for idx in top_indices:
        listing_id = int(listing_ids[idx])
        score = float(scores[idx])
        listing = df[df['id'] == listing_id].iloc[0]
        
        results.append({
            'listing_id': listing_id,
            'score': round(score, 4),
            'name': listing['name'],
            'neighbourhood': listing['neighbourhood_cleansed'],
            'url': listing['listing_url'],
            'photo_url': f'{os.getenv("PHOTO_BASE_URL", "http://localhost:8000")}/photos/{city}/{listing_id}.jpg',
        })
    
    return results


# Pre-load Barcelona at startup so first request is fast
_load_city_data('barcelona')
print("Ready.")


# === Allow running this file directly to test ===
if __name__ == '__main__':
    print("\n--- Test search ---")
    test_image = Image.open('images/test.png')
    results = search(test_image, city='barcelona')
    for rank, r in enumerate(results, start=1):
        print(f"{rank:2}. ({r['score']:.4f}) {r['name'][:50]:50}  {r['url']}")