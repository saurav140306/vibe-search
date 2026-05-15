"""
Download photos for a city's listings.

Usage:
    python download_photos.py <city> [num_photos]

Example:
    python download_photos.py lisbon 500

Expects:
    data/<city>/listings_clean.csv

Produces:
    data/<city>/photos/<listing_id>.jpg  (resized to 512px max)
"""

import sys
import os
import pandas as pd
import requests
import time
from PIL import Image
from io import BytesIO


def download_photos(city: str, num_to_download: int = 500):
    city_dir = os.path.join('data', city)
    csv_path = os.path.join(city_dir, 'listings_clean.csv')
    photos_dir = os.path.join(city_dir, 'photos')
    
    if not os.path.exists(csv_path):
        print(f"ERROR: {csv_path} not found. Run prepare_city.py {city} first.")
        sys.exit(1)
    
    os.makedirs(photos_dir, exist_ok=True)
    
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} listings for {city}")
    
    DELAY_SECONDS = 0.5
    MAX_DIMENSION = 512
    
    batch = df.head(num_to_download)
    
    for index, row in batch.iterrows():
        listing_id = row['id']
        url = row['picture_url']
        output_path = os.path.join(photos_dir, f"{listing_id}.jpg")
        
        print(f"Downloading {listing_id}... ", end='', flush=True)
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            image = Image.open(BytesIO(response.content))
            image.thumbnail((MAX_DIMENSION, MAX_DIMENSION))
            image.convert('RGB').save(output_path, 'JPEG', quality=85)
            
            new_size_kb = os.path.getsize(output_path) / 1024
            print(f"saved ({new_size_kb:.0f} KB)")
        except Exception as e:
            print(f"FAILED: {e}")
        
        time.sleep(DELAY_SECONDS)
    
    print(f"\nDone. Photos saved to {photos_dir}/")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python download_photos.py <city> [num_photos]")
        sys.exit(1)
    
    city = sys.argv[1]
    num = int(sys.argv[2]) if len(sys.argv) > 2 else 500
    
    download_photos(city, num)