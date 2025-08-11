import uuid
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from . import models

# For this MVP, the commission is a fixed percentage
MARKETPLACE_COMMISSION_RATE = Decimal("0.10") # 10%

def _calculate_commission(total_amount: Decimal) -> Decimal:
    """Calculates the marketplace commission."""
    return total_amount * MARKETPLACE_COMMISSION_RATE

async def create_invoice_for_order(db: AsyncSession, order_details: dict):
    """
    This function is triggered by an 'order_completed' Kafka event.
    It creates an invoice and simulates the entire escrow and payout flow.
    """
    order_id = uuid.UUID(order_details["orderId"])
    client_org_id = uuid.UUID(order_details["clientId"])
    total_amount = Decimal(str(order_details["totalPrice"]))
    currency = order_details["currency"]

    # 1. Create an Invoice for the client
    new_invoice = models.Invoice(
        order_id=order_id,
        organization_id=client_org_id,
        amount=total_amount,
        currency=currency,
        status=models.InvoiceStatus.ISSUED
    )
    db.add(new_invoice)
    await db.commit()
    await db.refresh(new_invoice)
    print(f"Created invoice {new_invoice.id} for order {order_id}")

    # 2. Simulate the client paying the invoice into escrow
    payment_transaction = models.Transaction(
        invoice_id=new_invoice.id,
        transaction_type=models.TransactionType.PAYMENT,
        amount=total_amount,
        notes=f"Client payment for order {order_id}"
    )
    db.add(payment_transaction)
    new_invoice.status = models.InvoiceStatus.PAID
    await db.commit()
    print(f"Simulated client payment for invoice {new_invoice.id}")

    # 3. Calculate commission and create a transaction for it
    commission_amount = _calculate_commission(total_amount)
    commission_transaction = models.Transaction(
        invoice_id=new_invoice.id,
        transaction_type=models.TransactionType.COMMISSION,
        amount=commission_amount,
        notes=f"Marketplace commission for order {order_id}"
    )
    db.add(commission_transaction)
    await db.commit()
    print(f"Recorded commission of {commission_amount} for invoice {new_invoice.id}")

    # 4. Create a Payout record for the supplier
    payout_amount = total_amount - commission_amount
    supplier_org_id = uuid.UUID(order_details["supplier_organization_id"])

    new_payout = models.Payout(
        supplier_organization_id=supplier_org_id,
        order_id=order_id,
        amount=payout_amount,
        currency=currency,
        status=models.PayoutStatus.COMPLETED # Assuming instant payout for now
    )
    db.add(new_payout)
    await db.commit()
    await db.refresh(new_payout)
    print(f"Created Payout {new_payout.id} for supplier {supplier_org_id}")

    # 5. Create the final payout transaction, linked to the Payout record
    payout_transaction = models.Transaction(
        invoice_id=new_invoice.id,
        payout_id=new_payout.id,
        transaction_type=models.TransactionType.PAYOUT,
        amount=payout_amount,
        notes=f"Payout to supplier for order {order_id}"
    )
    db.add(payout_transaction)
    await db.commit()
    print(f"Recorded payout transaction for Payout {new_payout.id}")

    return new_invoice

async def get_invoices_by_organization(db: AsyncSession, org_id: uuid.UUID):
    result = await db.execute(
        select(models.Invoice)
        .where(models.Invoice.organization_id == org_id)
        .options(selectinload(models.Invoice.transactions))
        .order_by(models.Invoice.created_at.desc())
    )
    return result.scalars().all()

async def get_payouts_by_organization(db: AsyncSession, org_id: uuid.UUID):
    result = await db.execute(
        select(models.Payout)
        .where(models.Payout.supplier_organization_id == org_id)
        .order_by(models.Payout.created_at.desc())
    )
    return result.scalars().all()

async def mark_invoice_as_paid(db: AsyncSession, invoice_id: uuid.UUID, org_id: uuid.UUID):
    """
    Marks a given invoice as PAID. Includes an authorization check.
    """
    result = await db.execute(select(models.Invoice).where(models.Invoice.id == invoice_id))
    invoice = result.scalars().first()

    if not invoice:
        return None # Not found

    # Authz check
    if invoice.organization_id != org_id:
        return "unauthorized"

    invoice.status = models.InvoiceStatus.PAID
    await db.commit()
    await db.refresh(invoice)
    return invoice
