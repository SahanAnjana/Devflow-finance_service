# hr-service/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.base import Base
from app.db.session import engine
from app.api.budget import router as budget_router
from app.api.expense import router as expense_router
from app.api.invoice import router as invoice_router
from app.api.transaction import router as transaction_router
from app.api.account import router as account_router
from app.api.report import router as report_router

app = FastAPI(title="Finance Service API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (adjust for production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Include routers with appropriate prefixes
app.include_router(budget_router, prefix="/budgets", tags=["budgets"])
app.include_router(expense_router, prefix="/expenses", tags=["expenses"])
app.include_router(invoice_router, prefix="/invoices", tags=["invoices"])
app.include_router(transaction_router, prefix="/transactions", tags=["transactions"])
app.include_router(account_router, prefix="/accounts", tags=["accounts"])
app.include_router(report_router, prefix="/reports", tags=["reports"])

def create_tables():
    Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def startup_event():
    create_tables()

@app.get("/health")
def health_check():
    return {"status": "ok"}