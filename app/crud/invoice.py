# app/crud/invoice.py
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from app.db.models.models import (Invoice, InvoiceItem, PaymentStatus)

# Invoice CRUD operations
def create_invoice(db: Session, invoice_data) -> Invoice:
    # Generate sequential invoice number
    latest_invoice = db.query(Invoice).order_by(desc(Invoice.created_at)).first()
    next_number = 1
    if latest_invoice and latest_invoice.invoice_number:
        # Extract number part if invoice number is like "INV-0001"
        try:
            next_number = int(latest_invoice.invoice_number.split('-')[1]) + 1
        except (IndexError, ValueError):
            next_number = 1
    
    invoice_number = f"INV-{next_number:04d}"
    
    # Calculate totals
    subtotal = sum(item.quantity * item.unit_price for item in invoice_data.items)
    tax_amount = invoice_data.tax_amount if invoice_data.tax_amount is not None else 0.0
    total_amount = subtotal + tax_amount
    
    # Create invoice
    db_invoice = Invoice(
        id=str(uuid.uuid4()),
        invoice_number=invoice_number,
        client_id=invoice_data.client_id,
        project_id=invoice_data.project_id,
        issue_date=invoice_data.issue_date or datetime.utcnow(),
        due_date=invoice_data.due_date,
        amount=subtotal,
        tax_amount=tax_amount,
        total_amount=total_amount,
        status=PaymentStatus.PENDING,
        description=invoice_data.description,
        notes=invoice_data.notes,
    )
    
    db.add(db_invoice)
    db.flush()  # Flush to get the invoice ID without committing
    
    # Create invoice items
    for item in invoice_data.items:
        db_item = InvoiceItem(
            id=str(uuid.uuid4()),
            invoice_id=db_invoice.id,
            description=item.description,
            quantity=item.quantity,
            unit_price=item.unit_price,
            amount=item.quantity * item.unit_price
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(db_invoice)
    return db_invoice

def get_invoices(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    client_id: Optional[str] = None,
    project_id: Optional[str] = None,
    status: Optional[PaymentStatus] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None
) -> List[Invoice]:
    query = db.query(Invoice)
    
    # Apply filters
    if client_id:
        query = query.filter(Invoice.client_id == client_id)
    if project_id:
        query = query.filter(Invoice.project_id == project_id)
    if status:
        query = query.filter(Invoice.status == status)
    if from_date:
        query = query.filter(Invoice.issue_date >= from_date)
    if to_date:
        query = query.filter(Invoice.issue_date <= to_date)
    
    # Apply pagination
    return query.order_by(desc(Invoice.created_at)).offset(skip).limit(limit).all()

def get_invoice_by_id(db: Session, invoice_id: str) -> Optional[Invoice]:
    return db.query(Invoice).filter(Invoice.id == invoice_id).first()

def get_invoice_by_number(db: Session, invoice_number: str) -> Optional[Invoice]:
    return db.query(Invoice).filter(Invoice.invoice_number == invoice_number).first()

def update_invoice(db: Session, invoice_id: str, invoice_data) -> Optional[Invoice]:
    db_invoice = get_invoice_by_id(db, invoice_id)
    if not db_invoice:
        return None
    
    # Update invoice fields if provided
    update_data = invoice_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None and key != 'tax_amount':  # Handle tax_amount separately
            setattr(db_invoice, key, value)
    
    # Handle tax amount separately to recalculate total
    if 'tax_amount' in update_data and update_data['tax_amount'] is not None:
        db_invoice.tax_amount = update_data['tax_amount']
        db_invoice.total_amount = db_invoice.amount + db_invoice.tax_amount
    
    db_invoice.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_invoice)
    return db_invoice

def delete_invoice(db: Session, invoice_id: str) -> bool:
    db_invoice = get_invoice_by_id(db, invoice_id)
    if not db_invoice:
        return False
    
    db.delete(db_invoice)
    db.commit()
    return True

def mark_invoice_paid(db: Session, invoice_id: str) -> Optional[Invoice]:
    db_invoice = get_invoice_by_id(db, invoice_id)
    if not db_invoice:
        return None
    
    db_invoice.status = PaymentStatus.PAID
    db_invoice.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_invoice)
    return db_invoice