## Finance Service API Structure

### Core Finance Modules

1. **Invoices** - For client billing
2. **Expenses** - For tracking company expenses 
3. **Budgets** - For project and department budget management
4. **Transactions** - For tracking financial transactions
5. **Reports** - For financial reporting and analytics

### API Endpoints Design

```
/api/finance/
  ├── /invoices/                   # Invoice management
  │   ├── GET /                    # List all invoices (with filters)
  │   ├── POST /                   # Create a new invoice
  │   ├── GET /{id}                # Get invoice details
  │   ├── PUT /{id}                # Update invoice
  │   ├── DELETE /{id}             # Delete invoice
  │   ├── POST /{id}/send          # Send invoice to client
  │   ├── POST /{id}/mark-paid     # Mark invoice as paid
  │   └── GET /client/{client_id}  # Get invoices for a client
  │
  ├── /expenses/                   # Expense management
  │   ├── GET /                    # List all expenses (with filters)
  │   ├── POST /                   # Create a new expense
  │   ├── GET /{id}                # Get expense details
  │   ├── PUT /{id}                # Update expense
  │   ├── DELETE /{id}             # Delete expense
  │   ├── POST /{id}/approve       # Approve expense
  │   ├── POST /{id}/reject        # Reject expense
  │   └── GET /employee/{emp_id}   # Get expenses for an employee
  │
  ├── /budgets/                    # Budget management
  │   ├── GET /                    # List all budgets
  │   ├── POST /                   # Create a new budget
  │   ├── GET /{id}                # Get budget details
  │   ├── PUT /{id}                # Update budget 
  │   ├── DELETE /{id}             # Delete budget
  │   ├── GET /project/{proj_id}   # Get budget for a project
  │   └── GET /department/{dept_id}# Get budget for a department
  │
  ├── /transactions/               # Transaction tracking
  │   ├── GET /                    # List all transactions (with filters)
  │   ├── POST /                   # Record a new transaction
  │   ├── GET /{id}                # Get transaction details
  │   └── GET /account/{account_id}# Get transactions for an account
  │
  └── /reports/                    # Financial reporting
      ├── GET /summary             # Get financial summary
      ├── GET /profit-loss         # Get profit and loss report
      ├── GET /revenue             # Get revenue report
      ├── GET /expenses            # Get expenses report
      └── GET /project/{proj_id}   # Get financial report for a project
```

