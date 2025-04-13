# app/services/finance_reports.py
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.db.models.models import Invoice, Expense, Budget, Transaction, PaymentStatus, ExpenseStatus
from app.schemas import (FinancialSummary, ProfitLossReport, RevenueReport, ExpenseReport, ProjectFinanceReport)
from app.crud.report import (
    get_financial_summary_data,
    get_profit_loss_data,
    get_revenue_data,
    get_expense_data,
    get_project_finance_data
)
from app.schemas import InvoiceResponse, ExpenseResponse


def generate_financial_summary(db: Session, from_date: datetime, to_date: datetime) -> FinancialSummary:
    """
    Generate a financial summary report for the specified period.
    
    Args:
        db: Database session
        from_date: Start date for the report period
        to_date: End date for the report period
        
    Returns:
        FinancialSummary object containing summary financial data
    """
    # Get raw data from the database
    summary_data = get_financial_summary_data(db, from_date, to_date)
    
    # Return formatted report
    return FinancialSummary(
        total_income=summary_data["total_income"],
        total_expenses=summary_data["total_expenses"],
        net_profit=summary_data["net_profit"],
        pending_invoices=summary_data["pending_invoices"],
        overdue_invoices=summary_data["overdue_invoices"],
        period_start=from_date,
        period_end=to_date,
        generated_at=datetime.utcnow()
    )

def generate_profit_loss_report(db: Session, from_date: datetime, to_date: datetime) -> ProfitLossReport:
    """
    Generate a profit and loss report for the specified period.
    
    Args:
        db: Database session
        from_date: Start date for the report period
        to_date: End date for the report period
        
    Returns:
        ProfitLossReport object containing categorized income and expense data
    """
    # Get raw data from the database
    profit_loss_data = get_profit_loss_data(db, from_date, to_date)
    
    # Return formatted report - use the correct field names from the schema
    return ProfitLossReport(
        income=profit_loss_data["income"],  # These should be dictionaries, not lists
        expenses=profit_loss_data["expenses"],
        net_profit=profit_loss_data["net_profit"],
        period_start=from_date,
        period_end=to_date,
        generated_at=datetime.utcnow()
    )

def generate_revenue_report(db: Session, from_date: datetime, to_date: datetime) -> RevenueReport:
    """
    Generate a revenue report for the specified period.
    
    Args:
        db: Database session
        from_date: Start date for the report period
        to_date: End date for the report period
        
    Returns:
        RevenueReport object containing detailed revenue data
    """
    # Get raw data from the database
    revenue_data = get_revenue_data(db, from_date, to_date)
    
    # Return formatted report
    return RevenueReport(
        total_revenue=revenue_data["total_revenue"],
        by_client=revenue_data["by_client"],
        by_project=revenue_data["by_project"],
        by_month=revenue_data["by_month"],
        period_start=from_date,
        period_end=to_date,
        generated_at=datetime.utcnow()
    )

def generate_expense_report(db: Session, from_date: datetime, to_date: datetime) -> ExpenseReport:
    # Get raw data from the database
    expense_data = get_expense_data(db, from_date, to_date)
    
    # Return formatted report
    return ExpenseReport(
        total_expenses=expense_data["total_expenses"],
        by_category=expense_data["by_category"],
        by_employee=expense_data["by_employee"],
        by_project=expense_data["by_project"],
        by_month=expense_data["by_month"],
        period_start=from_date,
        period_end=to_date,
        generated_at=datetime.utcnow()
    )

def generate_project_finance_report(db: Session, project_id: str, from_date: datetime, to_date: datetime) -> ProjectFinanceReport:
    """
    Generate a financial report for a specific project.
    
    Args:
        db: Database session
        project_id: ID of the project
        from_date: Start date for the report period
        to_date: End date for the report period
        
    Returns:
        ProjectFinanceReport object containing detailed financial data for the project
    """
    # Get raw data from the database
    project_data = get_project_finance_data(db, project_id, from_date, to_date)
    
    # Convert invoice model objects to InvoiceResponse objects
    invoices = [
        InvoiceResponse(
            id=invoice.id,
            client_id=invoice.client_id,
            project_id=invoice.project_id,
            invoice_number=invoice.invoice_number,
            issue_date=invoice.issue_date,
            due_date=invoice.due_date,
            amount=invoice.amount,
            tax_amount=invoice.tax_amount,
            total_amount=invoice.total_amount,
            status=invoice.status,
            description=invoice.description,
            notes=invoice.notes,
            created_at=invoice.created_at,
            updated_at=invoice.updated_at,
            items=[]  # If you need items, you would need to fetch and include them
        )
        for invoice in project_data["invoices"]
    ]
    
    # Convert expense model objects to ExpenseResponse objects
    expenses = [
        ExpenseResponse(
            id=expense.id,
            employee_id=expense.employee_id,
            category=expense.category,
            amount=expense.amount,
            currency=expense.currency,
            description=expense.description,
            receipt_url=expense.receipt_url,
            expense_date=expense.expense_date,
            project_id=expense.project_id,
            department_id=expense.department_id,
            status=expense.status,
            approved_by=expense.approved_by,
            approved_at=expense.approved_at,
            created_at=expense.created_at,
            updated_at=expense.updated_at
        )
        for expense in project_data["expenses"]
    ]
    
    # Return formatted report
    return ProjectFinanceReport(
        project_id=project_id,
        project_name=project_data["project_name"],
        total_revenue=project_data["total_revenue"],
        total_expenses=project_data["total_expenses"],
        profit=project_data["profit"],
        budget_amount=project_data["budget_amount"],
        budget_remaining=project_data["budget_remaining"],
        invoices=invoices,
        expenses=expenses,
        period_start=from_date,
        period_end=to_date,
        generated_at=datetime.utcnow()
    )