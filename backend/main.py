from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth
from database import engine, Base

app = FastAPI(title="Re:Kite API")

# Create database tables
Base.metadata.create_all(bind=engine)

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

@app.get("/")
def read_root():
    return {"message": "Welcome to Re:Kite API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
