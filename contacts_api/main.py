import uvicorn
from fastapi import FastAPI, Depends
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from src.database.db import Base, engine
from src.routes import auth, contacts
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis

# Create FastAPI app instance
app = FastAPI()

# Define allowed origins for CORS
origins = [
    "http://localhost:8000",
]

# Add CORS middleware to the application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create all database tables
Base.metadata.create_all(bind=engine)

# Include the contacts and auth routers
app.include_router(contacts.router, prefix="/contacts")
app.include_router(auth.router, prefix="/api")

@app.on_event("startup")
async def startup():
    # Startup event handler to initialize Redis and FastAPILimiter.
    r = await redis.Redis(host='localhost', port=6379, db=0, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(r)

@app.get("/", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def root():
    # Root endpoint with rate limiting.
    # Returns a welcome message.
    return {"message": "Welcome to the contacts application."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

