# app/schemas/finance.py
from typing import List, Optional, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
import uuid
from enum import Enum

# Enums
class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class ExpenseStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REIMBURSED = "reimbursed"

# Invoice schemas
class InvoiceItemBase(BaseModel):
    description: str
    quantity: float = 1.0
    unit_price: float
    amount: Optional[float] = None

    @validator('amount', pre=True, always=True)
    def calculate_amount(cls, v, values):
        if v is None and 'quantity' in values and 'unit_price' in values:
            return values['quantity'] * values['unit_price']
        return v

class InvoiceItemCreate(InvoiceItemBase):
    pass

class InvoiceItemUpdate(BaseModel):
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    amount: Optional[float] = None

class InvoiceItemResponse(InvoiceItemBase):
    id: str
    invoice_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class InvoiceBase(BaseModel):
    client_id: str
    project_id: Optional[str] = None
    issue_date: Optional[datetime] = None
    due_date: datetime
    description: Optional[str] = None
    notes: Optional[str] = None

class InvoiceCreate(InvoiceBase):
    items: List[InvoiceItemCreate]
    tax_amount: Optional[float] = 0.0

class InvoiceUpdate(BaseModel):
    client_id: Optional[str] = None
    project_id: Optional[str] = None
    issue_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    status: Optional[PaymentStatus] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    tax_amount: Optional[float] = None

class InvoiceResponse(InvoiceBase):
    id: str
    invoice_number: str
    amount: float
    tax_amount: float
    total_amount: float
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime
    items: List[InvoiceItemResponse] = []

    class Config:
        orm_mode = True

# Expense schemas
class ExpenseBase(BaseModel):
    employee_id: str
    category: str
    amount: float
    currency: str = "USD"
    description: Optional[str] = None
    receipt_url: Optional[str] = None
    expense_date: datetime
    project_id: Optional[str] = None
    department_id: Optional[str] = None

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(BaseModel):
    category: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    description: Optional[str] = None
    receipt_url: Optional[str] = None
    expense_date: Optional[datetime] = None
    project_id: Optional[str] = None
    department_id: Optional[str] = None

class ExpenseResponse(ExpenseBase):
    id: str
    status: ExpenseStatus
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Budget schemas
class BudgetItemBase(BaseModel):
    category: str
    description: Optional[str] = None
    amount: float

class BudgetItemCreate(BudgetItemBase):
    pass

class BudgetItemUpdate(BaseModel):
    category: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = None

class BudgetItemResponse(BudgetItemBase):
    id: str
    budget_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class BudgetBase(BaseModel):
    name: str
    description: Optional[str] = None
    amount: float
    start_date: datetime
    end_date: datetime
    project_id: Optional[str] = None
    department_id: Optional[str] = None
    created_by: str

class BudgetCreate(BudgetBase):
    items: List[BudgetItemCreate]

class BudgetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class BudgetResponse(BudgetBase):
    id: str
    created_at: datetime
    updated_at: datetime
    items: List[BudgetItemResponse] = []

    class Config:
        orm_mode = True

# Transaction schemas
class TransactionBase(BaseModel):
    transaction_type: str  # income, expense, transfer
    amount: float
    currency: str = "USD"
    description: Optional[str] = None
    transaction_date: datetime
    account_id: str
    category: str
    reference_number: Optional[str] = None
    invoice_id: Optional[str] = None
    expense_id: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    description: Optional[str] = None
    category: Optional[str] = None
    reference_number: Optional[str] = None

class TransactionResponse(TransactionBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Account schemas
class AccountBase(BaseModel):
    name: str
    account_type: str  # bank, cash, credit card
    account_number: Optional[str] = None
    currency: str = "USD"
    balance: float = 0.0
    is_active: bool = True

class AccountCreate(AccountBase):
    pass

class AccountUpdate(BaseModel):
    name: Optional[str] = None
    account_number: Optional[str] = None
    is_active: Optional[bool] = None
    balance: Optional[float] = None

class AccountResponse(AccountBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Report Schemas
class FinancialSummary(BaseModel):
    total_income: float
    total_expenses: float
    net_profit: float
    pending_invoices: float
    overdue_invoices: float
    period_start: datetime
    period_end: datetime

class ProfitLossReport(BaseModel):
    income: dict
    expenses: dict
    net_profit: float
    period_start: datetime
    period_end: datetime

class RevenueReport(BaseModel):
    total_revenue: float
    by_client: dict
    by_project: dict
    by_month: dict
    period_start: datetime
    period_end: datetime

class ExpenseReport(BaseModel):
    total_expenses: float
    by_category: dict
    by_employee: dict
    by_project: dict
    by_month: dict
    period_start: datetime
    period_end: datetime

class ProjectFinanceReport(BaseModel):
    project_id: str
    project_name: str
    total_revenue: float
    total_expenses: float
    profit: float
    budget_amount: float
    budget_remaining: float
    invoices: List[InvoiceResponse]
    expenses: List[ExpenseResponse]
    period_start: datetime
    period_end: datetime