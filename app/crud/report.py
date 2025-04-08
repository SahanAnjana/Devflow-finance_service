# app/crud/report.py
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from sqlalchemy.sql import label

from app.db.models.models import (Invoice, Expense, Budget, Transaction, PaymentStatus, ExpenseStatus)

# Report data retrieval functions
def get_financial_summary_data(db: Session, from_date: datetime, to_date: datetime) -> Dict[str, Any]:
    """
    Retrieve data for the financial summary report.
    """
    # Calculate total income (paid invoices)
    income_query = db.query(func.sum(Invoice.total_amount)).filter(
        Invoice.status == PaymentStatus.PAID,
        Invoice.issue_date >= from_date,
        Invoice.issue_date <= to_date
    )
    total_income = income_query.scalar() or 0.0
    
    # Calculate total expenses
    expense_query = db.query(func.sum(Expense.amount)).filter(
        Expense.status == ExpenseStatus.APPROVED,
        Expense.expense_date >= from_date,
        Expense.expense_date <= to_date
    )
    total_expenses = expense_query.scalar() or 0.0
    
    # Calculate pending invoices
    pending_query = db.query(func.sum(Invoice.total_amount)).filter(
        Invoice.status == PaymentStatus.PENDING,
        Invoice.issue_date <= to_date
    )
    pending_invoices = pending_query.scalar() or 0.0
    
    # Calculate overdue invoices
    overdue_query = db.query(func.sum(Invoice.total_amount)).filter(
        Invoice.status == PaymentStatus.OVERDUE,
        Invoice.issue_date <= to_date
    )
    overdue_invoices = overdue_query.scalar() or 0.0
    
    # Net profit
    net_profit = total_income - total_expenses
    
    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_profit": net_profit,
        "pending_invoices": pending_invoices,
        "overdue_invoices": overdue_invoices,
        "period_start": from_date,
        "period_end": to_date
    }

def get_profit_loss_data(db: Session, from_date: datetime, to_date: datetime) -> Dict[str, Any]:
    """
    Retrieve data for the profit and loss report.
    """
    # Income by category (e.g., from invoice items)
    income_by_category = {}
    income_transactions = db.query(
        Transaction.category,
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.transaction_type == 'income',
        Transaction.transaction_date >= from_date,
        Transaction.transaction_date <= to_date
    ).group_by(Transaction.category).all()
    
    for category, total in income_transactions:
        income_by_category[category] = float(total)
    
    # Expenses by category
    expense_by_category = {}
    expense_query = db.query(
        Expense.category,
        func.sum(Expense.amount).label('total')
    ).filter(
        Expense.status == ExpenseStatus.APPROVED,
        Expense.expense_date >= from_date,
        Expense.expense_date <= to_date
    ).group_by(Expense.category).all()
    
    for category, total in expense_query:
        expense_by_category[category] = float(total)
    
    # Calculate totals
    total_income = sum(income_by_category.values())
    total_expenses = sum(expense_by_category.values())
    net_profit = total_income - total_expenses
    
    return {
        "income": income_by_category,
        "expenses": expense_by_category,
        "net_profit": net_profit,
        "period_start": from_date,
        "period_end": to_date
    }

def get_revenue_data(db: Session, from_date: datetime, to_date: datetime) -> Dict[str, Any]:
    """
    Retrieve data for the revenue report.
    """
    # Total revenue (from paid invoices)
    revenue_query = db.query(func.sum(Invoice.total_amount)).filter(
        Invoice.status == PaymentStatus.PAID,
        Invoice.issue_date >= from_date,
        Invoice.issue_date <= to_date
    )
    total_revenue = revenue_query.scalar() or 0.0
    
    # Revenue by client
    client_revenue = {}
    client_query = db.query(
        Invoice.client_id,
        func.sum(Invoice.total_amount).label('total')
    ).filter(
        Invoice.status == PaymentStatus.PAID,
        Invoice.issue_date >= from_date,
        Invoice.issue_date <= to_date
    ).group_by(Invoice.client_id).all()
    
    for client_id, total in client_query:
        client_revenue[client_id] = float(total)
    
    # Revenue by project
    project_revenue = {}
    project_query = db.query(
        Invoice.project_id,
        func.sum(Invoice.total_amount).label('total')
    ).filter(
        Invoice.project_id.isnot(None),
        Invoice.status == PaymentStatus.PAID,
        Invoice.issue_date >= from_date,
        Invoice.issue_date <= to_date
    ).group_by(Invoice.project_id).all()
    
    for project_id, total in project_query:
        project_revenue[project_id] = float(total)
    
    # Revenue by month
    month_revenue = {}
    month_query = db.query(
        func.date_trunc('month', Invoice.issue_date).label('month'),
        func.sum(Invoice.total_amount).label('total')
    ).filter(
        Invoice.status == PaymentStatus.PAID,
        Invoice.issue_date >= from_date,
        Invoice.issue_date <= to_date
    ).group_by('month').order_by('month').all()
    
    for month, total in month_query:
        month_key = month.strftime('%Y-%m')
        month_revenue[month_key] = float(total)
    
    return {
        "total_revenue": total_revenue,
        "by_client": client_revenue,
        "by_project": project_revenue,
        "by_month": month_revenue,
        "period_start": from_date,
        "period_end": to_date
    }

def get_expense_data(db: Session, from_date: datetime, to_date: datetime) -> Dict[str, Any]:
    """
    Retrieve data for the expense report.
    """
    # Total expenses
    expense_query = db.query(func.sum(Expense.amount)).filter(
        Expense.status == ExpenseStatus.APPROVED,
        Expense.expense_date >= from_date,
        Expense.expense_date <= to_date
    )
    total_expenses = expense_query.scalar() or 0.0
    
    # Expenses by category
    category_expenses = {}
    category_query = db.query(
        Expense.category,
        func.sum(Expense.amount).label('total')
    ).filter(
        Expense.status == ExpenseStatus.APPROVED,
        Expense.expense_date >= from_date,
        Expense.expense_date <= to_date
    ).group_by(Expense.category).all()
    
    for category, total in category_query:
        category_expenses[category] = float(total)
    
    # Expenses by employee
    employee_expenses = {}
    employee_query = db.query(
        Expense.employee_id,
        func.sum(Expense.amount).label('total')
    ).filter(
        Expense.status == ExpenseStatus.APPROVED,
        Expense.expense_date >= from_date,
        Expense.expense_date <= to_date
    ).group_by(Expense.employee_id).all()
    
    for employee_id, total in employee_query:
        employee_expenses[employee_id] = float(total)
    
    # Expenses by project
    project_expenses = {}
    project_query = db.query(
        Expense.project_id,
        func.sum(Expense.amount).label('total')
    ).filter(
        Expense.project_id.isnot(None),
        Expense.status == ExpenseStatus.APPROVED,
        Expense.expense_date >= from_date,
        Expense.expense_date <= to_date
    ).group_by(Expense.project_id).all()
    
    for project_id, total in project_query:
        project_expenses[project_id] = float(total)
    
    # Expenses by month
    month_expenses = {}
    month_query = db.query(
        func.date_trunc('month', Expense.expense_date).label('month'),
        func.sum(Expense.amount).label('total')
    ).filter(
        Expense.status == ExpenseStatus.APPROVED,
        Expense.expense_date >= from_date,
        Expense.expense_date <= to_date
    ).group_by('month').order_by('month').all()
    
    for month, total in month_query:
        month_key = month.strftime('%Y-%m')
        month_expenses[month_key] = float(total)
    
    return {
        "total_expenses": total_expenses,
        "by_category": category_expenses,
        "by_employee": employee_expenses,
        "by_project": project_expenses,
        "by_month": month_expenses,
        "period_start": from_date,
        "period_end": to_date
    }

def get_project_finance_data(db: Session, project_id: str, from_date: datetime, to_date: datetime) -> Dict[str, Any]:
    """
    Retrieve financial data for a specific project.
    """
    # Get project info (assuming a project table exists, otherwise would need to be passed in)
    project_name = f"Project {project_id}"  # This would be replaced with a query to get the actual name
    
    # Total revenue for the project
    revenue_query = db.query(func.sum(Invoice.total_amount)).filter(
        Invoice.project_id == project_id,
        Invoice.status == PaymentStatus.PAID,
        Invoice.issue_date >= from_date,
        Invoice.issue_date <= to_date
    )
    total_revenue = revenue_query.scalar() or 0.0
    
    # Total expenses for the project
    expense_query = db.query(func.sum(Expense.amount)).filter(
        Expense.project_id == project_id,
        Expense.status == ExpenseStatus.APPROVED,
        Expense.expense_date >= from_date,
        Expense.expense_date <= to_date
    )
    total_expenses = expense_query.scalar() or 0.0
    
    # Profit
    profit = total_revenue - total_expenses
    
    # Budget for the project
    budget_query = db.query(Budget).filter(
        Budget.project_id == project_id,
        Budget.start_date <= to_date,
        Budget.end_date >= from_date
    ).order_by(desc(Budget.created_at)).first()
    
    budget_amount = 0.0
    budget_remaining = 0.0
    if budget_query:
        budget_amount = budget_query.amount
        budget_remaining = budget_amount - total_expenses
    
    # Get all invoices for the project in the period
    invoices = db.query(Invoice).filter(
        Invoice.project_id == project_id,
        Invoice.issue_date >= from_date,
        Invoice.issue_date <= to_date
    ).all()
    
    # Get all expenses for the project in the period
    expenses = db.query(Expense).filter(
        Expense.project_id == project_id,
        Expense.expense_date >= from_date,
        Expense.expense_date <= to_date
    ).all()
    
    return {
        "project_id": project_id,
        "project_name": project_name,
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "profit": profit,
        "budget_amount": budget_amount,
        "budget_remaining": budget_remaining,
        "invoices": invoices,
        "expenses": expenses,
        "period_start": from_date,
        "period_end": to_date
    }