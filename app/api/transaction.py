# app/api/transaction.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.db.session import get_db
from app.schemas import (TransactionCreate, TransactionResponse)
from app.crud.transaction import (create_transaction, get_transactions, get_transaction_by_id)

router = APIRouter(prefix="/finance/transaction", tags=["transaction"])

# Transaction Management Endpoints
@router.get("/", response_model=List[TransactionResponse])
def list_transactions(
    account_id: Optional[str] = None,
    transaction_type: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List all transactions with optional filtering.
    """
    transactions = get_transactions(
        db, 
        skip=skip, 
        limit=limit,
        account_id=account_id,
        transaction_type=transaction_type,
        from_date=from_date,
        to_date=to_date
    )
    return transactions

@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_new_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    """
    Record a new transaction.
    """
    return create_transaction(db, transaction)

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: str = Path(..., description="The ID of the transaction to retrieve"), db: Session = Depends(get_db)):
    """
    Get details of a specific transaction.
    """
    db_transaction = get_transaction_by_id(db, transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction

@router.get("/account/{account_id}", response_model=List[TransactionResponse])
def get_account_transactions(
    account_id: str = Path(..., description="The ID of the account"),
    transaction_type: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get all transactions for a specific account.
    """
    transactions = get_transactions(
        db, 
        skip=skip, 
        limit=limit,
        account_id=account_id,
        transaction_type=transaction_type,
        from_date=from_date,
        to_date=to_date
    )
    return transactions