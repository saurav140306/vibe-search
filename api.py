from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image
from io import BytesIO
import os

from search import search

app = FastAPI(title="Vibe Search API")

# Allow requests from any origin (including HF Spaces and Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve photos for each city
# URL pattern: /photos/{city}/{listing_id}.jpg -> data/{city}/photos/{listing_id}.jpg
for city in os.listdir('data'):
    city_photos = os.path.join('data', city, 'photos')
    if os.path.isdir(city_photos):
        app.mount(f"/photos/{city}", StaticFiles(directory=city_photos), name=f"photos_{city}")


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Vibe Search API is running"}


@app.post("/search")
async def search_endpoint(file: UploadFile = File(...), city: str = "barcelona", top_k: int = 10):
    """
    Upload an image and get back the top_k most visually similar listings in the chosen city.
    """
    contents = await file.read()
    image = Image.open(BytesIO(contents))
    
    try:
        results = search(image, city=city, top_k=top_k)
    except ValueError as e:
        return {"error": str(e)}
    
    return {
        "query_filename": file.filename,
        "city": city,
        "num_results": len(results),
        "results": results,
    }