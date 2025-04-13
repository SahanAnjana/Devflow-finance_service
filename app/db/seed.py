# finance-service/app/db/seed.py
import random
from datetime import datetime, timedelta
from typing import List
import uuid
from faker import Faker
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from decimal import Decimal

from app.db.session import SessionLocal
from app.crud import (
    account,
    budget,
    expense,
    invoice,
    transaction
)
from app.schemas import (
    AccountCreate,
    BudgetCreate,
    BudgetItemCreate,
    ExpenseCreate,
    InvoiceCreate,
    TransactionCreate,
    ExpenseStatus,
    PaymentStatus
)

fake = Faker()

def seed_accounts(db: Session) -> List:
    """Seed financial accounts with dummy data."""
    accounts_data = [
        {"name": "Operating Account", "account_number": "ACT-1001", "account_type": "Checking", "balance": 250000.00, "is_active": True},
        {"name": "Payroll Account", "account_number": "ACT-1002", "account_type": "Checking", "balance": 85000.00, "is_active": True},
        {"name": "Tax Reserve", "account_number": "ACT-1003", "account_type": "Savings", "balance": 45000.00, "is_active": True},
        {"name": "Emergency Fund", "account_number": "ACT-1004", "account_type": "Savings", "balance": 100000.00, "is_active": True},
        {"name": "Capital Expenditure", "account_number": "ACT-1005", "account_type": "Investment", "balance": 150000.00, "is_active": True},
        {"name": "Petty Cash", "account_number": "ACT-1006", "account_type": "Cash", "balance": 2000.00, "is_active": True},
    ]
    
    accounts = []
    for acct_data in accounts_data:
        # Check if account already exists
        existing_acct = account.get_account_by_number(db, acct_data["account_number"])
        if existing_acct:
            print(f"Account '{acct_data['name']}' already exists, skipping...")
            accounts.append(existing_acct)
        else:
            try:
                acct = account.create_account(db, AccountCreate(**acct_data))
                accounts.append(acct)
                print(f"Created account: {acct_data['name']}")
            except IntegrityError:
                db.rollback()
                # Try to fetch it if creation failed due to race condition
                existing_acct = account.get_account_by_number(db, acct_data["account_number"])
                if existing_acct:
                    accounts.append(existing_acct)
                    print(f"Account '{acct_data['name']}' already exists (race condition), using existing...")
    
    return accounts

def seed_budgets(db: Session) -> List:
    """Seed budgets with dummy data."""
    budgets_data = [
        {"name": "Marketing Q2 2024", "amount": 75000.00, "start_date": datetime(2024, 4, 1), "end_date": datetime(2024, 6, 30), "project_id": "PRJ-001", "department_id": "DEPT-004"},
        {"name": "IT Infrastructure", "amount": 120000.00, "start_date": datetime(2024, 1, 1), "end_date": datetime(2024, 12, 31), "project_id": "PRJ-002", "department_id": "DEPT-002"},
        {"name": "HR Recruiting", "amount": 35000.00, "start_date": datetime(2024, 1, 1), "end_date": datetime(2024, 12, 31), "project_id": None, "department_id": "DEPT-001"},
        {"name": "Product Development", "amount": 250000.00, "start_date": datetime(2024, 1, 1), "end_date": datetime(2024, 12, 31), "project_id": "PRJ-003", "department_id": "DEPT-005"},
        {"name": "Office Maintenance", "amount": 18000.00, "start_date": datetime(2024, 1, 1), "end_date": datetime(2024, 12, 31), "project_id": None, "department_id": "DEPT-001"},
        {"name": "Staff Training", "amount": 40000.00, "start_date": datetime(2024, 1, 1), "end_date": datetime(2024, 12, 31), "project_id": None, "department_id": None},
    ]
    
    # Define categories for budget items
    categories = ["Salaries", "Equipment", "Software", "Travel", "Services", "Supplies", "Marketing", "Miscellaneous"]
    
    budgets = []
    for budget_data in budgets_data:
        # Create a unique code for each budget
        budget_code = f"BDG-{fake.unique.random_int(min=1000, max=9999)}"
        
        # Check if budget already exists
        existing_budget = budget.get_budget_by_name(db, budget_data["name"])
        if existing_budget:
            print(f"Budget '{budget_data['name']}' already exists, skipping...")
            budgets.append(existing_budget)
        else:
            try:
                # Create 2-5 budget items for each budget
                num_items = random.randint(2, 5)
                items = []
                remaining_amount = budget_data["amount"]
                
                for i in range(num_items):
                    # For the last item, use the remaining amount
                    if i == num_items - 1:
                        item_amount = remaining_amount
                    else:
                        # Allocate a random percentage of the remaining amount
                        percentage = random.uniform(0.1, 0.4)
                        item_amount = round(remaining_amount * percentage, 2)
                        remaining_amount -= item_amount
                    
                    items.append(BudgetItemCreate(
                        category=random.choice(categories),
                        description=fake.sentence(),
                        amount=item_amount
                    ))
                
                bdg = budget.create_budget(
                    db, 
                    BudgetCreate(
                        **budget_data,
                        budget_code=budget_code,
                        description=f"Budget for {budget_data['name']}",
                        notes=fake.sentence(),
                        created_by="ADMIN",
                        items=items  # Add the items list here
                    )
                )
                budgets.append(bdg)
                print(f"Created budget: {budget_data['name']}")
            except IntegrityError:
                db.rollback()
                # Try to fetch it if creation failed due to race condition
                existing_budget = budget.get_budget_by_name(db, budget_data["name"])
                if existing_budget:
                    budgets.append(existing_budget)
                    print(f"Budget '{budget_data['name']}' already exists (race condition), using existing...")
    
    return budgets

def seed_expenses(db: Session) -> List:
    """Seed expenses with dummy data."""
    # Check existing expenses count
    existing_count = len(expense.get_expenses(db))
    
    expenses = []
    if existing_count > 20:
        print(f"Already have {existing_count} expenses, skipping creation...")
        # Fetch existing expenses
        expenses = expense.get_expenses(db, limit=100)
    else:
        print("Creating expenses...")
        
        # Sample data for expenses
        expense_categories = ["Travel", "Office Supplies", "Software", "Hardware", "Training", "Consulting", "Marketing", "Utilities"]
        department_ids = ["DEPT-001", "DEPT-002", "DEPT-003", "DEPT-004", "DEPT-005"]
        project_ids = [None, "PRJ-001", "PRJ-002", "PRJ-003"]
        employee_ids = ["EMP-001", "EMP-002", "EMP-003", "EMP-004", "EMP-005", "EMP-006", "EMP-007"]
        
        # Create 25 random expenses
        for _ in range(25):
            category = random.choice(expense_categories)
            amount = round(random.uniform(10, 5000), 2)
            
            exp = expense.create_expense(db, ExpenseCreate(
                amount=amount,
                category=category,
                description=fake.sentence(),
                expense_date=fake.date_between(start_date="-180d", end_date="today"),
                employee_id=random.choice(employee_ids),
                department_id=random.choice(department_ids),
                project_id=random.choice(project_ids),
                receipt_url=f"/fake/receipts/{uuid.uuid4()}.pdf" if random.random() > 0.3 else None,
                status=random.choice(list(ExpenseStatus)),
                notes=fake.sentence() if random.random() > 0.5 else None,
                approved_by=random.choice(["EMP-001", "EMP-002"]) if random.random() > 0.6 else None,
                approved_date=datetime.utcnow() - timedelta(days=random.randint(1, 30)) if random.random() > 0.6 else None
            ))
            expenses.append(exp)
            print(f"Created expense: {category} - ${amount}")
    
    return expenses

def seed_invoices(db: Session) -> List:
    """Seed invoices with dummy data."""
    # Check existing invoices count
    existing_count = len(invoice.get_invoices(db))
    
    invoices = []
    if existing_count > 15:
        print(f"Already have {existing_count} invoices, skipping creation...")
        # Fetch existing invoices
        invoices = invoice.get_invoices(db, limit=100)
    else:
        print("Creating invoices...")
        
        # Sample data for invoices
        client_ids = ["CLT-001", "CLT-002", "CLT-003", "CLT-004", "CLT-005"]
        project_ids = [None, "PRJ-001", "PRJ-002", "PRJ-003"]
        
        # Create 20 random invoices
        for i in range(1, 21):
            invoice_number = f"INV-{2024}-{i:04d}"
            amount = round(random.uniform(1000, 50000), 2)
            
            # Make sure we're working with datetime objects, not date objects
            issue_date = fake.date_time_between(start_date="-180d", end_date=datetime.now())
            due_date = issue_date + timedelta(days=random.choice([15, 30, 45]))
            
            # Current time as datetime for comparison
            now = datetime.now()
            
            # Determine payment status based on due date
            if issue_date < now - timedelta(days=60):
                status = PaymentStatus.PAID
                paid_date = issue_date + timedelta(days=random.randint(1, 30))
            elif issue_date < now - timedelta(days=30):
                status = random.choice([PaymentStatus.PAID, PaymentStatus.OVERDUE])
                paid_date = issue_date + timedelta(days=random.randint(1, 30)) if status == PaymentStatus.PAID else None
            elif due_date < now:
                status = random.choice([PaymentStatus.PAID, PaymentStatus.PENDING, PaymentStatus.OVERDUE])
                paid_date = issue_date + timedelta(days=random.randint(1, 15)) if status == PaymentStatus.PAID else None
            else:
                status = PaymentStatus.PENDING
                paid_date = None
            
            # Create invoice items (required by InvoiceCreate schema)
            num_items = random.randint(1, 5)
            items = []
            remaining_amount = amount
            
            for j in range(num_items):
                # For the last item, use the remaining amount
                if j == num_items - 1:
                    item_amount = remaining_amount
                    quantity = 1
                    unit_price = item_amount
                else:
                    # Allocate a random percentage of the remaining amount
                    percentage = random.uniform(0.1, 0.4)
                    item_amount = round(remaining_amount * percentage, 2)
                    remaining_amount -= item_amount
                    
                    # Random quantity and calculate unit price
                    quantity = random.randint(1, 10)
                    unit_price = round(item_amount / quantity, 2)
                
                items.append({
                    "description": fake.sentence(),
                    "quantity": quantity,
                    "unit_price": unit_price
                })
                
            try:
                inv = invoice.create_invoice(db, InvoiceCreate(
                    invoice_number=invoice_number,
                    client_id=random.choice(client_ids),
                    project_id=random.choice(project_ids),
                    amount=amount,
                    issue_date=issue_date,
                    due_date=due_date,
                    status=status,
                    description=f"Services rendered for {fake.bs()}",
                    notes=fake.sentence() if random.random() > 0.5 else None,
                    paid_date=paid_date,
                    created_by="ADMIN",
                    items=items,
                    tax_amount=round(amount * 0.1, 2)  # 10% tax
                ))
                invoices.append(inv)
                print(f"Created invoice: {invoice_number} - ${amount}")
            except Exception as e:
                db.rollback()
                print(f"Error creating invoice {invoice_number}: {e}")
                continue
    
    return invoices

def seed_transactions(db: Session, accounts: List) -> List:
    """Seed financial transactions."""
    # Check existing transactions count
    existing_count = len(transaction.get_transactions(db))
    
    transactions = []
    if existing_count > 30:
        print(f"Already have {existing_count} transactions, skipping creation...")
        # Fetch existing transactions
        transactions = transaction.get_transactions(db, limit=100)
    else:
        print("Creating transactions...")
        
        # Transaction types
        transaction_types = ["Deposit", "Withdrawal", "Transfer", "Payment", "Refund", "Interest"]
        
        # Create 50 random transactions
        for _ in range(50):
            acct = random.choice(accounts)
            trans_type = random.choice(transaction_types)
            
            # Amount depends on transaction type
            if trans_type in ["Deposit", "Payment", "Refund", "Interest"]:
                amount = round(random.uniform(100, 10000), 2)
            else:  # Withdrawal or Transfer
                amount = round(random.uniform(-10000, -100), 2)
            
            # Create transaction data - note the change from 'date' to 'transaction_date'
            transaction_data = {
                "account_id": acct.id,
                "transaction_type": trans_type,
                "amount": amount,
                "description": f"{trans_type} - {fake.bs()}",
                "transaction_date": fake.date_between(start_date="-365d", end_date="today"),
                "reference_number": f"TX-{fake.unique.random_int(min=10000, max=99999)}",
                "category": random.choice(["Operational", "Payroll", "Investment", "Tax", "Vendor", "Client"])
            }
            
            # Add notes conditionally
            if random.random() > 0.7:
                transaction_data["notes"] = fake.sentence()
                
            # Handle destination account for transfers
            if trans_type == "Transfer":
                destination_options = [a.id for a in accounts if a.id != acct.id]
                if destination_options:
                    # This would require updating your schema to include this field
                    # Or you need to handle it differently in your create_transaction function
                    transaction_data["destination_account_id"] = random.choice(destination_options)
            
            try:
                trans = transaction.create_transaction(db, TransactionCreate(**transaction_data))
                transactions.append(trans)
                print(f"Created transaction: {trans_type} - ${abs(amount)}")
            except Exception as e:
                db.rollback()
                print(f"Error creating transaction: {e}")
                continue
    
    return transactions

def main():
    print("Starting finance database seeding...")
    db = SessionLocal()
    
    try:
        # Seed financial data
        print("\n=== Seeding Accounts ===")
        accounts = seed_accounts(db)
        
        print("\n=== Seeding Budgets ===")
        budgets = seed_budgets(db)
        
        print("\n=== Seeding Expenses ===")
        expenses = seed_expenses(db)
        
        print("\n=== Seeding Invoices ===")
        invoices = seed_invoices(db)
        
        print("\n=== Seeding Transactions ===")
        transactions = seed_transactions(db, accounts)
        
        print("\n=== Finance Database Seeding Summary ===")
        print(f"Accounts: {len(accounts)}")
        print(f"Budgets: {len(budgets)}")
        print(f"Expenses: {len(expenses)}")
        print(f"Invoices: {len(invoices)}")
        print(f"Transactions: {len(transactions)}")
        print("\nFinance database seeded successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()