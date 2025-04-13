# app/api/invoice.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.db.session import get_db
from app.schemas import (InvoiceCreate, InvoiceUpdate, InvoiceResponse, PaymentStatus)
from app.crud.invoice import (create_invoice, get_invoices, get_invoice_by_id, update_invoice, delete_invoice, mark_invoice_paid)


router = APIRouter()

# Invoice Management Endpoints
@router.get("/", response_model=List[InvoiceResponse])
def list_invoices(
    client_id: Optional[str] = None,
    project_id: Optional[str] = None,
    status: Optional[PaymentStatus] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List all invoices with optional filtering.
    """
    invoices = get_invoices(
        db, 
        skip=skip, 
        limit=limit,
        client_id=client_id,
        project_id=project_id,
        status=status,
        from_date=from_date,
        to_date=to_date
    )
    return invoices

@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_new_invoice(invoice: InvoiceCreate, db: Session = Depends(get_db)):
    """
    Create a new invoice.
    """
    return create_invoice(db, invoice)

@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(invoice_id: str = Path(..., description="The ID of the invoice to retrieve"), db: Session = Depends(get_db)):
    """
    Get details of a specific invoice.
    """
    db_invoice = get_invoice_by_id(db, invoice_id)
    if db_invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return db_invoice

@router.put("/{invoice_id}", response_model=InvoiceResponse)
def update_existing_invoice(
    invoice_data: InvoiceUpdate, 
    invoice_id: str = Path(..., description="The ID of the invoice to update"), 
    db: Session = Depends(get_db)
):
    """
    Update an existing invoice.
    """
    db_invoice = update_invoice(db, invoice_id, invoice_data)
    if db_invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return db_invoice

@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_invoice(invoice_id: str = Path(..., description="The ID of the invoice to delete"), db: Session = Depends(get_db)):
    """
    Delete an invoice.
    """
    success = delete_invoice(db, invoice_id)
    if not success:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return None

@router.post("/{invoice_id}/send", response_model=InvoiceResponse)
def send_invoice_to_client(invoice_id: str = Path(..., description="The ID of the invoice to send"), db: Session = Depends(get_db)):
    """
    Send an invoice to a client via email.
    """
    db_invoice = get_invoice_by_id(db, invoice_id)
    if db_invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Here you would implement the logic to send the invoice
    # For example, calling an email service or notification system
    # This is a placeholder for the implementation
    
    # For now, just return the invoice
    return db_invoice

@router.post("/{invoice_id}/mark-paid", response_model=InvoiceResponse)
def mark_invoice_as_paid(invoice_id: str = Path(..., description="The ID of the invoice to mark as paid"), db: Session = Depends(get_db)):
    """
    Mark an invoice as paid.
    """
    db_invoice = mark_invoice_paid(db, invoice_id)
    if db_invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return db_invoice

@router.get("/client/{client_id}", response_model=List[InvoiceResponse])
def get_client_invoices(
    client_id: str = Path(..., description="The ID of the client"),
    status: Optional[PaymentStatus] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get all invoices for a specific client.
    """
    invoices = get_invoices(
        db, 
        skip=skip, 
        limit=limit,
        client_id=client_id,
        status=status,
        from_date=from_date,
        to_date=to_date
    )
    return invoices






