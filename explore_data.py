import pandas

df = pandas.read_csv('data/listings.csv.gz')

print(f"Original: {len(df)} listings, {len(df.columns)} columns")

# Keep only the columns we need
columns_we_want = ['id', 'listing_url', 'name', 'picture_url', 
                   'latitude', 'longitude', 'neighbourhood_cleansed']
df = df[columns_we_want]

print(f"After column filter: {len(df)} listings, {len(df.columns)} columns")

# Drop rows where picture_url is missing
df = df.dropna(subset=['picture_url'])
print(f"After dropping listings with no photo: {len(df)} listings")

# Save the cleaned data for future use
df.to_csv('data/listings_clean.csv', index=False)
print("\nSaved cleaned data to data/listings_clean.csv")