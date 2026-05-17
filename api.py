from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image
from io import BytesIO
import os
import traceback

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
    print(f"[DEBUG] Received file: {file.filename}, content_type: {file.content_type}")
    
    contents = await file.read()
    print(f"[DEBUG] File size: {len(contents)} bytes")
    
    try:
        image = Image.open(BytesIO(contents))
        print(f"[DEBUG] PIL opened image: format={image.format}, mode={image.mode}, size={image.size}")
    except Exception as e:
        print(f"[DEBUG] PIL failed: {type(e).__name__}: {e}")
        return {"error": f"Could not open image: {e}"}
    
    try:
        results = search(image, city=city, top_k=top_k)
    except Exception as e:
        print(f"[DEBUG] Search failed: {type(e).__name__}: {e}")
        traceback.print_exc()
        return {"error": str(e), "error_type": type(e).__name__}
    
    return {
        "query_filename": file.filename,
        "city": city,
        "num_results": len(results),
        "results": results,
    }