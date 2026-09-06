import random
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()
IMG_DIR = Path(__file__).parent / "downloads"
EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

app.mount("/static", StaticFiles(directory=IMG_DIR), name="static")

@app.get("/img")
async def random_img(request: Request):
    images = [p for p in IMG_DIR.iterdir() if p.is_file() and p.suffix.lower() in EXTS]
    if not images:
        raise HTTPException(404, "no imgs found")
    name = random.choice(images).name
    return {
        "filename": name,
        "url": str(request.url_for("static", path=name)),
    }