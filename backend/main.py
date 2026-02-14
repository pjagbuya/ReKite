from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, decks, cards, study
from database import engine, Base

app = FastAPI(title="Re:Kite API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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
