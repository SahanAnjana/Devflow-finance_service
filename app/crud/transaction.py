# app/crud/transaction.py
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from app.db.models.models import (Transaction, Account)

# Transaction CRUD operations
def create_transaction(db: Session, transaction_data) -> Transaction:
    db_transaction = Transaction(
        id=str(uuid.uuid4()),
        transaction_type=transaction_data.transaction_type,
        amount=transaction_data.amount,
        currency=transaction_data.currency,
        description=transaction_data.description,
        transaction_date=transaction_data.transaction_date,
        account_id=transaction_data.account_id,
        category=transaction_data.category,
        reference_number=transaction_data.reference_number,
        invoice_id=transaction_data.invoice_id,
        expense_id=transaction_data.expense_id
    )
    
    db.add(db_transaction)
    
    # Update account balance
    db_account = db.query(Account).filter(Account.id == transaction_data.account_id).first()
    if db_account:
        if transaction_data.transaction_type == 'income':
            db_account.balance += transaction_data.amount
        elif transaction_data.transaction_type == 'expense':
            db_account.balance -= transaction_data.amount
    
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_transactions(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    account_id: Optional[str] = None,
    transaction_type: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None
) -> List[Transaction]:
    query = db.query(Transaction)
    
    # Apply filters
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    if transaction_type:
        query = query.filter(Transaction.transaction_type == transaction_type)
    if from_date:
        query = query.filter(Transaction.transaction_date >= from_date)
    if to_date:
        query = query.filter(Transaction.transaction_date <= to_date)
    
    # Apply pagination
    return query.order_by(desc(Transaction.transaction_date)).offset(skip).limit(limit).all()

def get_transaction_by_id(db: Session, transaction_id: str) -> Optional[Transaction]:
    return db.query(Transaction).filter(Transaction.id == transaction_id).first()

# Account CRUD operations
def create_account(db: Session, account_data) -> Account:
    db_account = Account(
        id=str(uuid.uuid4()),
        name=account_data.name,
        account_type=account_data.account_type,
        account_number=account_data.account_number,
        currency=account_data.currency,
        balance=account_data.balance,
        is_active=account_data.is_active
    )
    
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def get_accounts(db: Session, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None) -> List[Account]:
    query = db.query(Account)
    
    # Apply filters
    if is_active is not None:
        query = query.filter(Account.is_active == is_active)
    
    # Apply pagination
    return query.offset(skip).limit(limit).all()

def get_account_by_id(db: Session, account_id: str) -> Optional[Account]:
    return db.query(Account).filter(Account.id == account_id).first()