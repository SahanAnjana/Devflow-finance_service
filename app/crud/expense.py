# app/crud/expense.py
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from app.db.models.models import (Expense, ExpenseStatus)


# Expense CRUD operations
def create_expense(db: Session, expense_data) -> Expense:
    db_expense = Expense(
        id=str(uuid.uuid4()),
        employee_id=expense_data.employee_id,
        category=expense_data.category,
        amount=expense_data.amount,
        currency=expense_data.currency,
        description=expense_data.description,
        receipt_url=expense_data.receipt_url,
        expense_date=expense_data.expense_date,
        project_id=expense_data.project_id,
        department_id=expense_data.department_id,
        status=ExpenseStatus.PENDING
    )
    
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

def get_expenses(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    employee_id: Optional[str] = None,
    project_id: Optional[str] = None,
    department_id: Optional[str] = None,
    status: Optional[ExpenseStatus] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None
) -> List[Expense]:
    query = db.query(Expense)
    
    # Apply filters
    if employee_id:
        query = query.filter(Expense.employee_id == employee_id)
    if project_id:
        query = query.filter(Expense.project_id == project_id)
    if department_id:
        query = query.filter(Expense.department_id == department_id)
    if status:
        query = query.filter(Expense.status == status)
    if from_date:
        query = query.filter(Expense.expense_date >= from_date)
    if to_date:
        query = query.filter(Expense.expense_date <= to_date)
    
    # Apply pagination
    return query.order_by(desc(Expense.created_at)).offset(skip).limit(limit).all()

def get_expense_by_id(db: Session, expense_id: str) -> Optional[Expense]:
    return db.query(Expense).filter(Expense.id == expense_id).first()

def update_expense(db: Session, expense_id: str, expense_data) -> Optional[Expense]:
    db_expense = get_expense_by_id(db, expense_id)
    if not db_expense:
        return None
    
    # Update expense fields if provided
    update_data = expense_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(db_expense, key, value)
    
    db_expense.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_expense)
    return db_expense

def delete_expense(db: Session, expense_id: str) -> bool:
    db_expense = get_expense_by_id(db, expense_id)
    if not db_expense:
        return False
    
    db.delete(db_expense)
    db.commit()
    return True

def approve_expense(db: Session, expense_id: str, approver_id: str) -> Optional[Expense]:
    db_expense = get_expense_by_id(db, expense_id)
    if not db_expense:
        return None
    
    db_expense.status = ExpenseStatus.APPROVED
    db_expense.approved_by = approver_id
    db_expense.approved_at = datetime.utcnow()
    db_expense.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_expense)
    return db_expense

def reject_expense(db: Session, expense_id: str, approver_id: str) -> Optional[Expense]:
    db_expense = get_expense_by_id(db, expense_id)
    if not db_expense:
        return None
    
    db_expense.status = ExpenseStatus.REJECTED
    db_expense.approved_by = approver_id
    db_expense.approved_at = datetime.utcnow()
    db_expense.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_expense)
    return db_expense