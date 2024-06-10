from fastapi import APIRouter, Depends, HTTPException, Security, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from src.repository import users as repository_users
from src.database.db import get_db
from src.schemas.user import UserModel, UserResponse, TokenSchema, RequestEmail
from src.services.auth import auth_service
from src.services.verification import send_email
import logging

router = APIRouter(prefix='/auth', tags=['auth'])

logger = logging.getLogger(__name__)

@router.post(path="/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, bt: BackgroundTasks, request: Request, db: AsyncSession = Depends(get_db)):
    logger.info("Checking if user exists")
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        logger.info("User already exists")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    logger.info("Creating new user")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    logger.info("New user created, sending email")
    # Send email
    bt.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    logger.info("Email sent")
    return {"user": new_user, "detail": "User successfully created"}

@router.post("/login", response_model=TokenSchema)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    logger.info("Logging in user")
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        logger.info("Invalid email")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.verification:
        logger.info("Email not verified")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not verification")
    if not auth_service.verify_password(body.password, user.password):
        logger.info("Invalid password")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    logger.info("User logged in")
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get('/refresh_token', response_model=TokenSchema)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(), db: AsyncSession = Depends(get_db)):
    logger.info("Refreshing token")
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        logger.info("Invalid refresh token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    logger.info("Token refreshed")
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    logger.info("Confirming email")
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        logger.info("Verification error: user not found")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.verification:
        logger.info("Email already confirmed")
        return {"message": "Your email is already confirmed"}
    await repository_users.verification_email(email, db)
    logger.info("Email confirmed")
    return {"message": "Email confirmed"}

@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: AsyncSession = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.email, db)

    if user.verification:
        return {"message": "Your email is already verification"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation."}