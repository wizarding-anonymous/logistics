import uuid
import enum
from sqlalchemy import Column, String, DateTime, func, Numeric, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .database import Base

class InvoiceStatus(str, enum.Enum):
    ISSUED = "issued"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class TransactionType(str, enum.Enum):
    PAYMENT = "payment"      # Client pays the invoice
    COMMISSION = "commission"  # Marketplace takes its cut
    PAYOUT = "payout"        # Payout to the supplier

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), nullable=False, index=True, unique=True)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    status = Column(SAEnum(InvoiceStatus), nullable=False, default=InvoiceStatus.ISSUED)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    transactions = relationship("Transaction", back_populates="invoice")

class PayoutStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class Payout(Base):
    __tablename__ = "payouts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supplier_organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    order_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False)
    status = Column(SAEnum(PayoutStatus), nullable=False, default=PayoutStatus.PENDING)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    completed_at = Column(DateTime, nullable=True)

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=True) # Can be null for direct payouts
    payout_id = Column(UUID(as_uuid=True), ForeignKey("payouts.id"), nullable=True)

    transaction_type = Column(SAEnum(TransactionType), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    notes = Column(String, nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    invoice = relationship("Invoice", back_populates="transactions")
