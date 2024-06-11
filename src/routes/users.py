import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, File, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_limiter.depends import RateLimiter

from src.repository import users as repository_users
from src.database.db import get_db
from src.schemas.user import UserDb
from src.entity.models import User
from src.services.auth import auth_service
from src.conf.config import config


router = APIRouter(prefix='/user', tags=['users'])


@router.get("/me/", response_model=UserDb, dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    return current_user

@router.patch('/avatar', response_model=UserDb, dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def update_avatar_user(file: UploadFile = File(), 
                             current_user: User = Depends(auth_service.get_current_user),
                             db: AsyncSession = Depends(get_db)
                             ):
    cloudinary.config(
        cloud_name=config.CLD_NAME,
        api_key=config.CLD_API_KEY,
        api_secret=config.CLD_API_SECRET,
        secure=True
    )

    r = cloudinary.uploader.upload(file.file, public_id=f'UsersApp/{current_user.username}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'UsersApp/{current_user.username}')\
                        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user