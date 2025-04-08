# app/api/account.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.session import get_db
from app.schemas import (AccountCreate, AccountUpdate, AccountResponse)
from app.crud.account import (create_account, get_accounts, get_account_by_id, update_account, delete_account)

router = APIRouter(prefix="/finance/accounts", tags=["accounts"])

# Account Management Endpoints
@router.get("/", response_model=List[AccountResponse])
def list_accounts(
    is_active: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List all accounts with optional filtering.
    """
    accounts = get_accounts(
        db, 
        skip=skip, 
        limit=limit,
        is_active=is_active
    )
    return accounts

@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_new_account(account: AccountCreate, db: Session = Depends(get_db)):
    """
    Create a new account.
    """
    return create_account(db, account)

@router.get("/{account_id}", response_model=AccountResponse)
def get_account(account_id: str = Path(..., description="The ID of the account to retrieve"), db: Session = Depends(get_db)):
    """
    Get details of a specific account.
    """
    db_account = get_account_by_id(db, account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_account

@router.put("/{account_id}", response_model=AccountResponse)
def update_existing_account(
    account_data: AccountUpdate, 
    account_id: str = Path(..., description="The ID of the account to update"), 
    db: Session = Depends(get_db)
):
    """
    Update an existing account.
    """
    db_account = update_account(db, account_id, account_data)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_account

@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_account(account_id: str = Path(..., description="The ID of the account to delete"), db: Session = Depends(get_db)):
    """
    Delete an account.
    """
    success = delete_account(db, account_id)
    if not success:
        raise HTTPException(status_code=404, detail="Account not found")
    return None

@router.put("/{account_id}/activate", response_model=AccountResponse)
def activate_account(
    account_id: str = Path(..., description="The ID of the account to activate"), 
    db: Session = Depends(get_db)
):
    """
    Activate an account.
    """
    account_update = AccountUpdate(is_active=True)
    db_account = update_account(db, account_id, account_update)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_account

@router.put("/{account_id}/deactivate", response_model=AccountResponse)
def deactivate_account(
    account_id: str = Path(..., description="The ID of the account to deactivate"), 
    db: Session = Depends(get_db)
):
    """
    Deactivate an account.
    """
    account_update = AccountUpdate(is_active=False)
    db_account = update_account(db, account_id, account_update)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_account