from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import items, audio 


app = FastAPI()
app.include_router(items.router)
app.include_router(audio.router)

# Add these lines before your endpoints
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Svelte's default port
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Working!"}

