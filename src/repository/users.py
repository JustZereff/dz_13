from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from libgravatar import Gravatar
from src.database.db import get_db
from src.entity.models import User
from src.schemas.user import UserModel, UserDb
import logging

logger = logging.getLogger(__name__)

async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    stmt = select(User).filter_by(email=email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    return user

async def create_user(body: UserDb, db: AsyncSession = Depends(get_db)):
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as err:
        logger.error(f"Error getting avatar: {err}")
    
    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
    
async def update_token(user: User, token: str, db: AsyncSession):
    user.refresh_token = token
    await db.commit()
    
async def verification_email(email: str, db: AsyncSession) -> None:
    user = await get_user_by_email(email, db)
    user.verification = True
    await db.commit()
