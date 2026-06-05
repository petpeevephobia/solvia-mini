import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api.v1 import router as v1_router
from app.config import settings

app = FastAPI(title="Solvia lead audits API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Keep your existing backend routes working
app.include_router(v1_router, prefix="/api/v1")

@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

# FIX: Explicitly point paths to the absolute /app container workspace
ROOT_DIR = "/app"
BACKEND_DIR = "/app/backend"

# Function to search for an asset folder path in the container
def find_folder(folder_name):
    paths_to_check = [os.path.join(ROOT_DIR, folder_name), os.path.join(BACKEND_DIR, folder_name)]
    for p in paths_to_check:
        if os.path.exists(p):
            return p
    return None

# Mount static folders cleanly based on where they actually exist inside Docker
css_path = find_folder("css")
if css_path:
    app.mount("/css", StaticFiles(directory=css_path), name="css")

js_path = find_folder("js")
if js_path:
    app.mount("/js", StaticFiles(directory=js_path), name="js")

assets_path = find_folder("assets")
if assets_path:
    app.mount("/assets", StaticFiles(directory=assets_path), name="assets")


# Serve your index.html dynamically
@app.get("/")
async def read_index():
    possible_index_locations = [
        os.path.join(ROOT_DIR, "index.html"),
        os.path.join(BACKEND_DIR, "index.html"),
        os.path.join(ROOT_DIR, "_site", "index.html")
    ]
    
    for path in possible_index_locations:
        if os.path.exists(path):
            return FileResponse(path)
            
    # Fallback debug screen if it still cannot find it
    debug_map = {
        "error": "index.html not found in expected paths.",
        "checked_paths": possible_index_locations,
        "root_contents": os.listdir(ROOT_DIR) if os.path.exists(ROOT_DIR) else "Not found",
        "backend_contents": os.listdir(BACKEND_DIR) if os.path.exists(BACKEND_DIR) else "Not found"
    }
    return debug_map