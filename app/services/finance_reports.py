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
    
    # Format income and expense categories for the report
    income_categories = [
        {"category": category, "amount": amount}
        for category, amount in profit_loss_data["income"].items()
    ]
    
    expense_categories = [
        {"category": category, "amount": amount}
        for category, amount in profit_loss_data["expenses"].items()
    ]
    
    # Return formatted report
    return ProfitLossReport(
        income_categories=income_categories,
        total_income=sum(item["amount"] for item in income_categories),
        expense_categories=expense_categories,
        total_expenses=sum(item["amount"] for item in expense_categories),
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
    
    # Format client revenue for the report
    client_revenue = [
        {"client_id": client_id, "amount": amount}
        for client_id, amount in revenue_data["by_client"].items()
    ]
    
    # Format project revenue for the report
    project_revenue = [
        {"project_id": project_id, "amount": amount}
        for project_id, amount in revenue_data["by_project"].items()
    ]
    
    # Format monthly revenue for the report
    monthly_revenue = [
        {"month": month, "amount": amount}
        for month, amount in revenue_data["by_month"].items()
    ]
    
    # Return formatted report
    return RevenueReport(
        total_revenue=revenue_data["total_revenue"],
        client_revenue=client_revenue,
        project_revenue=project_revenue,
        monthly_revenue=monthly_revenue,
        period_start=from_date,
        period_end=to_date,
        generated_at=datetime.utcnow()
    )

def generate_expense_report(db: Session, from_date: datetime, to_date: datetime) -> ExpenseReport:
    """
    Generate an expense report for the specified period.
    
    Args:
        db: Database session
        from_date: Start date for the report period
        to_date: End date for the report period
        
    Returns:
        ExpenseReport object containing detailed expense data
    """
    # Get raw data from the database
    expense_data = get_expense_data(db, from_date, to_date)
    
    # Format category expenses for the report
    category_expenses = [
        {"category": category, "amount": amount}
        for category, amount in expense_data["by_category"].items()
    ]
    
    # Format employee expenses for the report
    employee_expenses = [
        {"employee_id": employee_id, "amount": amount}
        for employee_id, amount in expense_data["by_employee"].items()
    ]
    
    # Format project expenses for the report
    project_expenses = [
        {"project_id": project_id, "amount": amount}
        for project_id, amount in expense_data["by_project"].items()
    ]
    
    # Format monthly expenses for the report
    monthly_expenses = [
        {"month": month, "amount": amount}
        for month, amount in expense_data["by_month"].items()
    ]
    
    # Return formatted report
    return ExpenseReport(
        total_expenses=expense_data["total_expenses"],
        category_expenses=category_expenses,
        employee_expenses=employee_expenses,
        project_expenses=project_expenses,
        monthly_expenses=monthly_expenses,
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
    
    # Convert invoice and expense model objects to appropriate format for the report
    invoices = [
        {
            "invoice_id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "issue_date": invoice.issue_date,
            "due_date": invoice.due_date,
            "amount": invoice.total_amount,
            "status": invoice.status.value
        }
        for invoice in project_data["invoices"]
    ]
    
    expenses = [
        {
            "expense_id": expense.id,
            "category": expense.category,
            "expense_date": expense.expense_date,
            "amount": expense.amount,
            "status": expense.status.value
        }
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