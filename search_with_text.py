from sentence_transformers import SentenceTransformer, util
from PIL import Image
import os

# Load the CLIP model
model = SentenceTransformer('clip-ViT-B-32')

# Embed all the images (same as last time)
image_folder = 'images'
image_files = os.listdir(image_folder)

image_embeddings = {}
for filename in image_files:
    full_path = os.path.join(image_folder, filename)
    image = Image.open(full_path)
    image_embeddings[filename] = model.encode(image)
    print(f"Embedded {filename}")

# Now embed a text query
query = "ancient monument"
query_embedding = model.encode(query)

# Compare the query to every image
print(f"\nQuery: '{query}'")
print("--- Best matches ---")
results = []
for filename, embedding in image_embeddings.items():
    score = util.cos_sim(query_embedding, embedding).item()
    results.append((filename, score))

# Sort by score, highest first
results.sort(key=lambda x: x[1], reverse=True)

for filename, score in results:
    print(f"{filename:12}  {score:.4f}")