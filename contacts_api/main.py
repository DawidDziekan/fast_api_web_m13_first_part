import uvicorn
from fastapi import FastAPI, Depends
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from contacts_api.src.database.db import Base, engine
from contacts_api.src.routes import auth, contacts
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis


app = FastAPI()

origins = [
    "http://localhost:8000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(contacts.router, prefix="/contacts")
app.include_router(auth.router, prefix="/api")

@app.on_event("startup")
async def startup():
    r = await redis.Redis(host='localhost', port=6379, db=0, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(r)

@app.get("/", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def root():
    return {"message": "Witaj w aplikacji kontaktowej."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
