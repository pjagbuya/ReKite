from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, decks, cards, study
from database import engine, Base
import os

app = FastAPI(title="Re:Kite API")

# Configure CORS - Allow frontend URLs
allowed_origins = [
    "http://localhost:3000",  # Local development
    "https://*.vercel.app",    # Vercel deployments
]

# Add production frontend URL from environment if set
if frontend_url := os.getenv("FRONTEND_URL"):
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",  # Allow all Vercel preview URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(decks.router, prefix="/api/decks", tags=["decks"])
app.include_router(cards.router, prefix="/api/cards", tags=["cards"])
app.include_router(study.router, prefix="/api/study", tags=["study"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Re:Kite API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
