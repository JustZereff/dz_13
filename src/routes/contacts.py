from fastapi import APIRouter, Query, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.repository import contacts as repositories_contact
from src.database.db import get_db
from src.schemas.contact import ContactInput, ContactOutput
from src.entity.models import User
from src.services.auth import auth_service

router = APIRouter(prefix='/contacts', tags=['contact'])

@router.get(path='/', response_model=list[ContactOutput])
async def get_contacts(limit: int = Query(default=10, ge=10, le=500), offset: int = Query(default=0), db: AsyncSession = Depends(get_db)):
    contacts = await repositories_contact.get_contacts(limit, offset, db)
    return contacts

@router.get(path='/id/{contact_id}', response_model=ContactOutput)
async def get_contacts_by_id(contact_id: int, db: AsyncSession = Depends(get_db)):
    contact = await repositories_contact.get_contact_by_id(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found!')
    return contact

@router.get(path='/first_name/{first_name}', response_model=list[ContactOutput])
async def get_contacts_by_first_name(first_name: str, db: AsyncSession = Depends(get_db)):
    contacts = await repositories_contact.get_contacts_by_first_name(first_name, db)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found!')
    return contacts

@router.get(path='/last_name/{last_name}', response_model=list[ContactOutput])
async def get_contacts_by_last_name(last_name: str, db: AsyncSession = Depends(get_db)):
    contacts = await repositories_contact.get_contacts_by_last_name(last_name, db)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found!')
    return contacts

@router.get(path='/email/{email}', response_model=ContactOutput)
async def get_contacts_by_email(email: str, db: AsyncSession = Depends(get_db)):
    contact = await repositories_contact.get_contact_by_email(email, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found!')
    return contact

@router.post('/', response_model=ContactOutput, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactInput, db: AsyncSession = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    contact = await repositories_contact.create_contact(body, current_user.id, db)
    return contact

@router.put('/id/{contact_id}', response_model=ContactOutput)
async def update_contact(contact_id: int, body: ContactInput, db: AsyncSession = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    contact = await repositories_contact.update_contact(contact_id, body, current_user.id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found or not authorized!')
    return contact

@router.delete('/id/{contact_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    contact = await repositories_contact.delete_contact(contact_id, current_user.id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found or not authorized!')
    return {"detail": "Contact deleted successfully"}

@router.get(path='/birthday/next_week', response_model=list[ContactOutput])
async def get_contacts_with_upcoming_birthdays(db: AsyncSession = Depends(get_db)):
    contacts = await repositories_contact.get_contacts_with_upcoming_birthdays(db)
    return contacts
