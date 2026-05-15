"""
Filter Inside Airbnb's raw listings.csv.gz into a clean CSV.

Usage:
    python prepare_city.py <city>

Example:
    python prepare_city.py lisbon

Expects:
    data/<city>/listings.csv.gz  (raw downloaded file)

Produces:
    data/<city>/listings_clean.csv
"""

import sys
import os
import pandas as pd


def prepare_city(city: str):
    city_dir = os.path.join('data', city)
    raw_path = os.path.join(city_dir, 'listings.csv.gz')
    clean_path = os.path.join(city_dir, 'listings_clean.csv')
    
    if not os.path.exists(raw_path):
        print(f"ERROR: Expected file not found: {raw_path}")
        print(f"Download listings.csv.gz from Inside Airbnb and put it in {city_dir}/")
        sys.exit(1)
    
    print(f"Loading {raw_path}...")
    df = pd.read_csv(raw_path)
    print(f"  Loaded {len(df)} listings, {len(df.columns)} columns")
    
    columns_we_want = ['id', 'listing_url', 'name', 'picture_url',
                       'latitude', 'longitude', 'neighbourhood_cleansed']
    df = df[columns_we_want]
    
    # Drop listings missing a photo URL
    df = df.dropna(subset=['picture_url'])
    print(f"  After cleanup: {len(df)} listings")
    
    df.to_csv(clean_path, index=False)
    print(f"Saved to {clean_path}")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python prepare_city.py <city>")
        print("Example: python prepare_city.py lisbon")
        sys.exit(1)
    
    prepare_city(sys.argv[1])