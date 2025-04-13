# app/api/report.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.db.session import get_db
from app.schemas import (FinancialSummary, ProfitLossReport, RevenueReport, ExpenseReport, ProjectFinanceReport)

# Additional imports for report generation
from app.services.finance_reports import (
    generate_financial_summary,
    generate_profit_loss_report,
    generate_revenue_report,
    generate_expense_report,
    generate_project_finance_report
)

router = APIRouter()

# Financial Reporting Endpoints
@router.get("/summary", response_model=FinancialSummary)
def get_financial_summary(
    from_date: Optional[datetime] = Query(None, description="Start date for the report period"),
    to_date: Optional[datetime] = Query(None, description="End date for the report period"),
    db: Session = Depends(get_db)
):
    """
    Get a financial summary report.
    """
    # Default to current month if dates not provided
    if not from_date:
        from_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if not to_date:
        # Last day of current month
        next_month = from_date.replace(day=28) + timedelta(days=4)
        to_date = next_month - timedelta(days=next_month.day)
    
    return generate_financial_summary(db, from_date, to_date)

@router.get("/profit-loss", response_model=ProfitLossReport)
def get_profit_loss_report(
    from_date: Optional[datetime] = Query(None, description="Start date for the report period"),
    to_date: Optional[datetime] = Query(None, description="End date for the report period"),
    db: Session = Depends(get_db)
):
    """
    Get a profit and loss report.
    """
    # Default to current month if dates not provided
    if not from_date:
        from_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if not to_date:
        # Last day of current month
        next_month = from_date.replace(day=28) + timedelta(days=4)
        to_date = next_month - timedelta(days=next_month.day)
    
    return generate_profit_loss_report(db, from_date, to_date)

@router.get("/revenue", response_model=RevenueReport)
def get_revenue_report(
    from_date: Optional[datetime] = Query(None, description="Start date for the report period"),
    to_date: Optional[datetime] = Query(None, description="End date for the report period"),
    db: Session = Depends(get_db)
):
    """
    Get a revenue report.
    """
    # Default to current month if dates not provided
    if not from_date:
        from_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if not to_date:
        # Last day of current month
        next_month = from_date.replace(day=28) + timedelta(days=4)
        to_date = next_month - timedelta(days=next_month.day)
    
    return generate_revenue_report(db, from_date, to_date)

@router.get("/expenses", response_model=ExpenseReport)
def get_expenses_report(
    from_date: Optional[datetime] = Query(None, description="Start date for the report period"),
    to_date: Optional[datetime] = Query(None, description="End date for the report period"),
    db: Session = Depends(get_db)
):
    """
    Get an expenses report.
    """
    # Default to current month if dates not provided
    if not from_date:
        from_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if not to_date:
        # Last day of current month
        next_month = from_date.replace(day=28) + timedelta(days=4)
        to_date = next_month - timedelta(days=next_month.day)
    
    return generate_expense_report(db, from_date, to_date)

@router.get("/project/{project_id}", response_model=ProjectFinanceReport)
def get_project_finance_report(
    project_id: str = Path(..., description="The ID of the project"),
    from_date: Optional[datetime] = Query(None, description="Start date for the report period"),
    to_date: Optional[datetime] = Query(None, description="End date for the report period"),
    db: Session = Depends(get_db)
):
    """
    Get a financial report for a specific project.
    """
    # Default to all time if dates not provided
    if not from_date:
        from_date = datetime(2000, 1, 1)  # A date far in the past
    if not to_date:
        to_date = datetime.now()
    
    return generate_project_finance_report(db, project_id, from_date, to_date)