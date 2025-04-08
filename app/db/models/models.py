# app/db/models/finance.py
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Float, Integer, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base import Base
import enum

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class ExpenseStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REIMBURSED = "reimbursed"

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    invoice_number = Column(String(50), unique=True, index=True)
    client_id = Column(String(36), index=True)
    project_id = Column(String(36), index=True, nullable=True)
    issue_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime)
    amount = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="invoice")

class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    invoice_id = Column(String(36), ForeignKey("invoices.id"))
    description = Column(String(255), nullable=False)
    quantity = Column(Float, default=1.0)
    unit_price = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    invoice = relationship("Invoice", back_populates="items")

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(String(36), index=True)
    category = Column(String(100), index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    description = Column(Text, nullable=True)
    receipt_url = Column(String(255), nullable=True)
    expense_date = Column(DateTime, nullable=False)
    status = Column(Enum(ExpenseStatus), default=ExpenseStatus.PENDING)
    approved_by = Column(String(36), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    project_id = Column(String(36), index=True, nullable=True)
    department_id = Column(String(36), index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    amount = Column(Float, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    project_id = Column(String(36), index=True, nullable=True)
    department_id = Column(String(36), index=True, nullable=True)
    created_by = Column(String(36), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    items = relationship("BudgetItem", back_populates="budget", cascade="all, delete-orphan")

class BudgetItem(Base):
    __tablename__ = "budget_items"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    budget_id = Column(String(36), ForeignKey("budgets.id"))
    category = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    budget = relationship("Budget", back_populates="items")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    transaction_type = Column(String(50), nullable=False)  # income, expense, transfer
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    description = Column(Text, nullable=True)
    transaction_date = Column(DateTime, nullable=False)
    account_id = Column(String(36), index=True, nullable=False)
    category = Column(String(100), index=True)
    reference_number = Column(String(100), nullable=True)
    invoice_id = Column(String(36), ForeignKey("invoices.id"), nullable=True)
    expense_id = Column(String(36), ForeignKey("expenses.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    invoice = relationship("Invoice", back_populates="transactions")

class Account(Base):
    __tablename__ = "accounts"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    account_type = Column(String(50), nullable=False)  # bank, cash, credit card
    account_number = Column(String(50), nullable=True)
    currency = Column(String(3), default="USD")
    balance = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)