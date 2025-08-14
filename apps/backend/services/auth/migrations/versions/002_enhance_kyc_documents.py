"""Enhance KYC documents with validation fields

Revision ID: 002
Revises: 001
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to kyc_documents table
    op.add_column('kyc_documents', sa.Column('file_name', sa.String(), nullable=True))
    op.add_column('kyc_documents', sa.Column('file_size', sa.Integer(), nullable=True))
    op.add_column('kyc_documents', sa.Column('file_hash', sa.String(), nullable=True))
    op.add_column('kyc_documents', sa.Column('mime_type', sa.String(), nullable=True))
    op.add_column('kyc_documents', sa.Column('virus_scan_status', sa.String(), nullable=True, default='pending'))
    op.add_column('kyc_documents', sa.Column('validation_status', sa.String(), nullable=True, default='pending'))
    op.add_column('kyc_documents', sa.Column('validation_errors', sa.Text(), nullable=True))
    op.add_column('kyc_documents', sa.Column('inn_validation_status', sa.String(), nullable=True))
    op.add_column('kyc_documents', sa.Column('ogrn_validation_status', sa.String(), nullable=True))
    op.add_column('kyc_documents', sa.Column('extracted_inn', sa.String(), nullable=True))
    op.add_column('kyc_documents', sa.Column('extracted_ogrn', sa.String(), nullable=True))
    op.add_column('kyc_documents', sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), nullable=True))
    
    # Update existing records with default values
    op.execute("UPDATE kyc_documents SET file_name = 'unknown.pdf' WHERE file_name IS NULL")
    op.execute("UPDATE kyc_documents SET file_size = 0 WHERE file_size IS NULL")
    op.execute("UPDATE kyc_documents SET file_hash = 'unknown' WHERE file_hash IS NULL")
    op.execute("UPDATE kyc_documents SET virus_scan_status = 'pending' WHERE virus_scan_status IS NULL")
    op.execute("UPDATE kyc_documents SET validation_status = 'pending' WHERE validation_status IS NULL")
    
    # Make required fields non-nullable
    op.alter_column('kyc_documents', 'file_name', nullable=False)
    op.alter_column('kyc_documents', 'file_size', nullable=False)
    op.alter_column('kyc_documents', 'file_hash', nullable=False)


def downgrade() -> None:
    # Remove added columns
    op.drop_column('kyc_documents', 'reviewed_by')
    op.drop_column('kyc_documents', 'extracted_ogrn')
    op.drop_column('kyc_documents', 'extracted_inn')
    op.drop_column('kyc_documents', 'ogrn_validation_status')
    op.drop_column('kyc_documents', 'inn_validation_status')
    op.drop_column('kyc_documents', 'validation_errors')
    op.drop_column('kyc_documents', 'validation_status')
    op.drop_column('kyc_documents', 'virus_scan_status')
    op.drop_column('kyc_documents', 'mime_type')
    op.drop_column('kyc_documents', 'file_hash')
    op.drop_column('kyc_documents', 'file_size')
    op.drop_column('kyc_documents', 'file_name')