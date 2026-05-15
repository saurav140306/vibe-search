from sentence_transformers import SentenceTransformer, util
from PIL import Image
import os

model = SentenceTransformer('clip-ViT-B-32') 
image_folder = 'images' 
image_files = os.listdir(image_folder)
print(f"Found {len(image_files)} files in {image_folder}")
embeddings = {}
for filename in image_files:
    full_path = os.path.join(image_folder, filename)
    image = Image.open(full_path)
    embedding = model.encode(image)
    embeddings[filename] = embedding
    print(f"Embedded {filename}")
print(f"\nDone. We have {len(embeddings)} embeddings stored")

print("\n Similarity Scores:")
filenames = list(embeddings.keys())
for i in range(len(filenames)):
    for j in range(i + 1, len(filenames)):
        name_a = filenames[i]
        name_b = filenames[j]
        score = util.cos_sim(embeddings[name_a], embeddings[name_b]).item()
        print(f"{name_a:12} <-> {name_b:12} {score:.4f}")