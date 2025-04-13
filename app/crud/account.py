# app/crud/account.py
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from app.db.models.models import Account

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


def get_account_by_number(db: Session, account_number: str) -> Optional[Account]:
    return db.query(Account).filter(Account.account_number == account_number).first()

def update_account(db: Session, account_id: str, account_data) -> Optional[Account]:
    db_account = get_account_by_id(db, account_id)
    if not db_account:
        return None
    
    # Update account fields if provided
    update_data = account_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(db_account, key, value)
    
    db_account.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_account)
    return db_account

def delete_account(db: Session, account_id: str) -> bool:
    db_account = get_account_by_id(db, account_id)
    if not db_account:
        return False
    
    db.delete(db_account)
    db.commit()
    return True

def update_account_balance(db: Session, account_id: str, amount: float, is_deposit: bool) -> Optional[Account]:
    db_account = get_account_by_id(db, account_id)
    if not db_account:
        return None
    
    if is_deposit:
        db_account.balance += amount
    else:
        db_account.balance -= amount
    
    db_account.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_account)
    return db_account