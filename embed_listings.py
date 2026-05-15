"""
Embed all photos for a city using CLIP, save to disk.

Usage:
    python embed_listings.py <city>

Example:
    python embed_listings.py lisbon

Expects:
    data/<city>/photos/  (folder of jpg files)

Produces:
    data/<city>/embeddings.npz
"""

import sys
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from PIL import Image


def embed_city(city: str):
    city_dir = os.path.join('data', city)
    photos_dir = os.path.join(city_dir, 'photos')
    embeddings_path = os.path.join(city_dir, 'embeddings.npz')
    
    if not os.path.isdir(photos_dir):
        print(f"ERROR: {photos_dir} not found. Run download_photos.py {city} first.")
        sys.exit(1)
    
    print("Loading CLIP model...")
    model = SentenceTransformer('clip-ViT-B-32')
    
    photo_files = os.listdir(photos_dir)
    print(f"Found {len(photo_files)} photos to embed for {city}")
    
    listing_ids = []
    embeddings = []
    
    for i, filename in enumerate(photo_files):
        listing_id = filename.replace('.jpg', '')
        full_path = os.path.join(photos_dir, filename)
        
        try:
            image = Image.open(full_path)
            embedding = model.encode(image)
            
            listing_ids.append(listing_id)
            embeddings.append(embedding)
            
            if (i + 1) % 50 == 0:
                print(f"  Embedded {i + 1}/{len(photo_files)}")
        except Exception as e:
            print(f"  FAILED on {filename}: {e}")
    
    print(f"\nEmbedded {len(embeddings)} photos total")
    
    embeddings_array = np.array(embeddings)
    np.savez(embeddings_path,
             listing_ids=np.array(listing_ids),
             embeddings=embeddings_array)
    
    print(f"Saved to {embeddings_path}")
    print(f"Embeddings shape: {embeddings_array.shape}")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python embed_listings.py <city>")
        sys.exit(1)
    
    embed_city(sys.argv[1])