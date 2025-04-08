# app/api/expense.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.db.session import get_db
from app.schemas import (ExpenseCreate, ExpenseUpdate, ExpenseResponse, ExpenseStatus)
from app.crud.expense import (create_expense, get_expenses, get_expense_by_id, update_expense, delete_expense, approve_expense, reject_expense)


router = APIRouter(prefix="/finance/expenses", tags=["expenses"])

# Expense Management Endpoints
@router.get("/", response_model=List[ExpenseResponse])
def list_expenses(
    employee_id: Optional[str] = None,
    project_id: Optional[str] = None,
    department_id: Optional[str] = None,
    status: Optional[ExpenseStatus] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List all expenses with optional filtering.
    """
    expenses = get_expenses(
        db, 
        skip=skip, 
        limit=limit,
        employee_id=employee_id,
        project_id=project_id,
        department_id=department_id,
        status=status,
        from_date=from_date,
        to_date=to_date
    )
    return expenses

@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_new_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    """
    Create a new expense.
    """
    return create_expense(db, expense)

@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(expense_id: str = Path(..., description="The ID of the expense to retrieve"), db: Session = Depends(get_db)):
    """
    Get details of a specific expense.
    """
    db_expense = get_expense_by_id(db, expense_id)
    if db_expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return db_expense

@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_existing_expense(
    expense_data: ExpenseUpdate, 
    expense_id: str = Path(..., description="The ID of the expense to update"), 
    db: Session = Depends(get_db)
):
    """
    Update an existing expense.
    """
    db_expense = update_expense(db, expense_id, expense_data)
    if db_expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return db_expense

@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_expense(expense_id: str = Path(..., description="The ID of the expense to delete"), db: Session = Depends(get_db)):
    """
    Delete an expense.
    """
    success = delete_expense(db, expense_id)
    if not success:
        raise HTTPException(status_code=404, detail="Expense not found")
    return None

@router.post("/{expense_id}/approve", response_model=ExpenseResponse)
def approve_existing_expense(
    expense_id: str = Path(..., description="The ID of the expense to approve"),
    approver_id: str = Query(..., description="The ID of the approver"),
    db: Session = Depends(get_db)
):
    """
    Approve an expense.
    """
    db_expense = approve_expense(db, expense_id, approver_id)
    if db_expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return db_expense

@router.post("/{expense_id}/reject", response_model=ExpenseResponse)
def reject_existing_expense(
    expense_id: str = Path(..., description="The ID of the expense to reject"),
    approver_id: str = Query(..., description="The ID of the approver"),
    db: Session = Depends(get_db)
):
    """
    Reject an expense.
    """
    db_expense = reject_expense(db, expense_id, approver_id)
    if db_expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return db_expense

@router.get("/employee/{employee_id}", response_model=List[ExpenseResponse])
def get_employee_expenses(
    employee_id: str = Path(..., description="The ID of the employee"),
    status: Optional[ExpenseStatus] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get all expenses for a specific employee.
    """
    expenses = get_expenses(
        db, 
        skip=skip, 
        limit=limit,
        employee_id=employee_id,
        status=status,
        from_date=from_date,
        to_date=to_date
    )
    return expenses