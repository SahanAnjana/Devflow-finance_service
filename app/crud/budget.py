# app/crud/budget.py
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from app.db.models.models import (Budget, BudgetItem)

# Budget CRUD operations
def create_budget(db: Session, budget_data) -> Budget:
    # Create budget
    db_budget = Budget(
        id=str(uuid.uuid4()),
        name=budget_data.name,
        description=budget_data.description,
        amount=budget_data.amount,
        start_date=budget_data.start_date,
        end_date=budget_data.end_date,
        project_id=budget_data.project_id,
        department_id=budget_data.department_id,
        created_by=budget_data.created_by
    )
    
    db.add(db_budget)
    db.flush()  # Flush to get the budget ID without committing
    
    # Create budget items
    for item in budget_data.items:
        db_item = BudgetItem(
            id=str(uuid.uuid4()),
            budget_id=db_budget.id,
            category=item.category,
            description=item.description,
            amount=item.amount
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(db_budget)
    return db_budget

def get_budgets(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    project_id: Optional[str] = None,
    department_id: Optional[str] = None
) -> List[Budget]:
    query = db.query(Budget)
    
    # Apply filters
    if project_id:
        query = query.filter(Budget.project_id == project_id)
    if department_id:
        query = query.filter(Budget.department_id == department_id)
    
    # Apply pagination
    return query.order_by(desc(Budget.created_at)).offset(skip).limit(limit).all()

def get_budget_by_id(db: Session, budget_id: str) -> Optional[Budget]:
    return db.query(Budget).filter(Budget.id == budget_id).first()

def get_budget_by_name(db: Session, name: str) -> Optional[Budget]:
    return db.query(Budget).filter(Budget.name == name).first()

def update_budget(db: Session, budget_id: str, budget_data) -> Optional[Budget]:
    db_budget = get_budget_by_id(db, budget_id)
    if not db_budget:
        return None
    
    # Update budget fields if provided
    update_data = budget_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(db_budget, key, value)
    
    db_budget.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_budget)
    return db_budget

def delete_budget(db: Session, budget_id: str) -> bool:
    db_budget = get_budget_by_id(db, budget_id)
    if not db_budget:
        return False
    
    db.delete(db_budget)
    db.commit()
    return True