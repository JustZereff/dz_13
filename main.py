from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter

from src.routes import contacts, auth, users
from src.database.db import get_db  
from src.conf.config import config  

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение маршрутов
app.include_router(auth.router, prefix='/api')
app.include_router(contacts.router, prefix='/api')
app.include_router(users.router, prefix='/api')

@app.on_event("startup")
async def startup():
    # Подключение к Redis
    r = await redis.Redis(
        host=config.redis_host,
        port=config.redis_port,
        db=0,
        password=config.redis_password,
        encoding="utf-8",
        decode_responses=True
    )
    await FastAPILimiter.init(r)

@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        # Проверка подключения к базе данных
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to healthchecker!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")

@app.get("/")
def index():
    return {"message": "Welcome to FastAPI!"}
