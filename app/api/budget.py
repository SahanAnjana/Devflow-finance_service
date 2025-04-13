# app/api/budget.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.db.session import get_db
from app.schemas import (BudgetCreate, BudgetUpdate, BudgetResponse)
from app.crud.budget import (create_budget, get_budgets, get_budget_by_id, update_budget, delete_budget)


router = APIRouter()

# Budget Management Endpoints
@router.get("/", response_model=List[BudgetResponse])
def list_budgets(
    project_id: Optional[str] = None,
    department_id: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List all budgets with optional filtering.
    """
    budgets = get_budgets(
        db, 
        skip=skip, 
        limit=limit,
        project_id=project_id,
        department_id=department_id
    )
    return budgets

@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_new_budget(budget: BudgetCreate, db: Session = Depends(get_db)):
    """
    Create a new budget.
    """
    return create_budget(db, budget)

@router.get("/{budget_id}", response_model=BudgetResponse)
def get_budget(budget_id: str = Path(..., description="The ID of the budget to retrieve"), db: Session = Depends(get_db)):
    """
    Get details of a specific budget.
    """
    db_budget = get_budget_by_id(db, budget_id)
    if db_budget is None:
        raise HTTPException(status_code=404, detail="Budget not found")
    return db_budget

@router.put("/{budget_id}", response_model=BudgetResponse)
def update_existing_budget(
    budget_data: BudgetUpdate, 
    budget_id: str = Path(..., description="The ID of the budget to update"), 
    db: Session = Depends(get_db)
):
    """
    Update an existing budget.
    """
    db_budget = update_budget(db, budget_id, budget_data)
    if db_budget is None:
        raise HTTPException(status_code=404, detail="Budget not found")
    return db_budget

@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_budget(budget_id: str = Path(..., description="The ID of the budget to delete"), db: Session = Depends(get_db)):
    """
    Delete a budget.
    """
    success = delete_budget(db, budget_id)
    if not success:
        raise HTTPException(status_code=404, detail="Budget not found")
    return None

@router.get("/project/{project_id}", response_model=List[BudgetResponse])
def get_project_budgets(
    project_id: str = Path(..., description="The ID of the project"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get all budgets for a specific project.
    """
    budgets = get_budgets(
        db, 
        skip=skip, 
        limit=limit,
        project_id=project_id
    )
    return budgets

@router.get("/department/{department_id}", response_model=List[BudgetResponse])
def get_department_budgets(
    department_id: str = Path(..., description="The ID of the department"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get all budgets for a specific department.
    """
    budgets = get_budgets(
        db, 
        skip=skip, 
        limit=limit,
        department_id=department_id
    )
    return budgets