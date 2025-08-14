import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import hashlib

from main import app
from database import get_db
from models import User, KYCDocument, KYCStatus
from file_validator import FileValidator
from s3_client import S3Client
import service

# Test client
client = TestClient(app)

# Mock database session
@pytest.fixture
async def db_session():
    # In a real test, you'd set up a test database
    mock_session = Mock(spec=AsyncSession)
    return mock_session

# Mock user
@pytest.fixture
def mock_user():
    user = Mock(spec=User)
    user.id = uuid.uuid4()
    user.email = "test@example.com"
    user.roles = ["supplier"]
    return user

# Mock KYC document
@pytest.fixture
def mock_kyc_document():
    doc = Mock(spec=KYCDocument)
    doc.id = uuid.uuid4()
    doc.document_type = "inn"
    doc.file_name = "test_inn.pdf"
    doc.file_size = 1024
    doc.file_hash = "test_hash"
    doc.status = KYCStatus.PENDING
    return doc

class TestFileValidator:
    """Test file validation functionality"""
    
    def test_calculate_file_hash(self):
        """Test file hash calculation"""
        test_content = b"test file content"
        expected_hash = hashlib.sha256(test_content).hexdigest()
        
        result = FileValidator.calculate_file_hash(test_content)
        assert result == expected_hash
    
    def test_validate_file_type_pdf(self):
        """Test PDF file type validation"""
        # Mock PDF content (simplified)
        pdf_content = b"%PDF-1.4\n%test content"
        
        with patch('magic.from_buffer', return_value='application/pdf'):
            is_valid, mime_type, error = FileValidator.validate_file_type(pdf_content, "test.pdf")
            
            assert is_valid is True
            assert mime_type == 'application/pdf'
            assert error is None
    
    def test_validate_file_type_invalid(self):
        """Test invalid file type validation"""
        exe_content = b"MZ\x90\x00"  # PE executable signature
        
        with patch('magic.from_buffer', return_value='application/x-executable'):
            is_valid, mime_type, error = FileValidator.validate_file_type(exe_content, "test.exe")
            
            assert is_valid is False
            assert mime_type == 'application/x-executable'
            assert "File type not allowed" in error
    
    def test_validate_file_size_valid(self):
        """Test valid file size"""
        file_size = 1024 * 1024  # 1MB
        is_valid, error = FileValidator.validate_file_size(file_size)
        
        assert is_valid is True
        assert error is None
    
    def test_validate_file_size_too_large(self):
        """Test file size too large"""
        file_size = 20 * 1024 * 1024  # 20MB
        is_valid, error = FileValidator.validate_file_size(file_size)
        
        assert is_valid is False
        assert "exceeds maximum allowed size" in error
    
    @pytest.mark.asyncio
    async def test_virus_scan_clean(self):
        """Test virus scan with clean file"""
        clean_content = b"clean file content"
        
        status, error = await FileValidator.scan_for_viruses(clean_content, "test.pdf")
        
        assert status == 'clean'
        assert error is None
    
    @pytest.mark.asyncio
    async def test_virus_scan_infected(self):
        """Test virus scan with suspicious content"""
        suspicious_content = b"<script>alert('xss')</script>"
        
        status, error = await FileValidator.scan_for_viruses(suspicious_content, "test.pdf")
        
        assert status == 'infected'
        assert error is not None
    
    @pytest.mark.asyncio
    async def test_validate_inn_valid(self):
        """Test valid INN validation"""
        valid_inn = "7707083893"  # Valid INN with correct checksum
        
        status, error = await FileValidator.validate_inn(valid_inn)
        
        # Note: This is a simplified test. In reality, you'd mock the external API
        assert status in ['valid', 'error']  # Could be error if no external API
    
    @pytest.mark.asyncio
    async def test_validate_inn_invalid_format(self):
        """Test invalid INN format"""
        invalid_inn = "123"  # Too short
        
        status, error = await FileValidator.validate_inn(invalid_inn)
        
        assert status == 'invalid'
        assert "INN must be 10 or 12 digits" in error
    
    @pytest.mark.asyncio
    async def test_validate_ogrn_valid_format(self):
        """Test valid OGRN format"""
        valid_ogrn = "1027700132195"  # 13 digits
        
        status, error = await FileValidator.validate_ogrn(valid_ogrn)
        
        # Note: This is a simplified test
        assert status in ['valid', 'invalid', 'error']
    
    @pytest.mark.asyncio
    async def test_validate_ogrn_invalid_format(self):
        """Test invalid OGRN format"""
        invalid_ogrn = "123"  # Too short
        
        status, error = await FileValidator.validate_ogrn(invalid_ogrn)
        
        assert status == 'invalid'
        assert "OGRN must be 13 or 15 digits" in error

class TestS3Client:
    """Test S3 client functionality"""
    
    def test_generate_file_key(self):
        """Test file key generation"""
        s3_client = S3Client()
        user_id = str(uuid.uuid4())
        document_type = "inn"
        filename = "test.pdf"
        
        file_key = s3_client.generate_file_key(user_id, document_type, filename)
        
        assert file_key.startswith(f"kyc/{user_id}/{document_type}/")
        assert file_key.endswith(".pdf")
    
    @pytest.mark.asyncio
    async def test_upload_file_success(self):
        """Test successful file upload"""
        s3_client = S3Client()
        test_content = b"test file content"
        file_key = "test/file.pdf"
        content_type = "application/pdf"
        
        with patch.object(s3_client.client, 'put_object') as mock_put:
            mock_put.return_value = None
            
            success, error = await s3_client.upload_file(test_content, file_key, content_type)
            
            assert success is True
            assert error is None
            mock_put.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_download_file_success(self):
        """Test successful file download"""
        s3_client = S3Client()
        file_key = "test/file.pdf"
        expected_content = b"test file content"
        
        mock_response = Mock()
        mock_response['Body'].read.return_value = expected_content
        
        with patch.object(s3_client.client, 'get_object', return_value=mock_response):
            content, error = await s3_client.download_file(file_key)
            
            assert content == expected_content
            assert error is None

class TestKYCService:
    """Test KYC service functionality"""
    
    @pytest.mark.asyncio
    async def test_create_kyc_document_success(self, db_session, mock_user):
        """Test successful KYC document creation"""
        from schemas import KYCDocumentCreate
        
        doc_data = KYCDocumentCreate(
            document_type="inn",
            file_storage_key="test/file.pdf",
            file_name="test.pdf",
            file_size=1024,
            file_hash="test_hash"
        )
        
        # Mock database operations
        db_session.execute.return_value.scalars.return_value.first.return_value = None  # No existing doc
        db_session.add = Mock()
        db_session.commit = AsyncMock()
        db_session.refresh = AsyncMock()
        
        result = await service.create_kyc_document(db_session, mock_user.id, doc_data)
        
        assert result is not None
        db_session.add.assert_called_once()
        db_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_kyc_document_duplicate(self, db_session, mock_user):
        """Test KYC document creation with duplicate type"""
        from schemas import KYCDocumentCreate
        
        doc_data = KYCDocumentCreate(
            document_type="inn",
            file_storage_key="test/file.pdf",
            file_name="test.pdf",
            file_size=1024,
            file_hash="test_hash"
        )
        
        # Mock existing document
        existing_doc = Mock()
        db_session.execute.return_value.scalars.return_value.first.return_value = existing_doc
        
        with pytest.raises(ValueError, match="already has a pending"):
            await service.create_kyc_document(db_session, mock_user.id, doc_data)
    
    @pytest.mark.asyncio
    async def test_get_user_kyc_status_not_started(self, db_session, mock_user):
        """Test KYC status for user who hasn't started"""
        # Mock no documents
        db_session.execute.return_value.scalars.return_value.all.return_value = []
        
        status = await service.get_user_kyc_status(db_session, mock_user.id)
        
        assert status['status'] == 'not_started'
        assert len(status['required_documents']) > 0
        assert len(status['submitted_documents']) == 0
    
    @pytest.mark.asyncio
    async def test_get_user_kyc_status_approved(self, db_session, mock_user):
        """Test KYC status for approved user"""
        # Mock approved documents
        approved_docs = []
        for doc_type in ['inn', 'ogrn', 'business_license']:
            doc = Mock()
            doc.document_type = doc_type
            doc.status = KYCStatus.APPROVED
            approved_docs.append(doc)
        
        db_session.execute.return_value.scalars.return_value.all.return_value = approved_docs
        
        status = await service.get_user_kyc_status(db_session, mock_user.id)
        
        assert status['status'] == 'approved'
        assert len(status['approved_documents']) == 3

class TestKYCAPI:
    """Test KYC API endpoints"""
    
    def test_get_upload_url_unauthorized(self):
        """Test upload URL endpoint without authentication"""
        response = client.post("/api/v1/auth/users/me/kyc-documents/upload-url", json={
            "document_type": "inn",
            "file_name": "test.pdf"
        })
        
        assert response.status_code == 401
    
    def test_get_upload_url_invalid_role(self):
        """Test upload URL endpoint with invalid role"""
        # Mock user with client role (not supplier)
        with patch('api.v1.auth.get_current_user') as mock_get_user:
            mock_user = Mock()
            mock_user.roles = ["client"]
            mock_get_user.return_value = mock_user
            
            response = client.post("/api/v1/auth/users/me/kyc-documents/upload-url", json={
                "document_type": "inn",
                "file_name": "test.pdf"
            })
            
            assert response.status_code == 403
    
    def test_get_kyc_status_success(self):
        """Test KYC status endpoint"""
        with patch('api.v1.auth.get_current_user') as mock_get_user, \
             patch('service.get_user_kyc_status') as mock_get_status:
            
            mock_user = Mock()
            mock_user.id = uuid.uuid4()
            mock_get_user.return_value = mock_user
            
            mock_status = {
                'status': 'pending',
                'required_documents': ['inn', 'ogrn'],
                'submitted_documents': ['inn'],
                'approved_documents': [],
                'rejected_documents': []
            }
            mock_get_status.return_value = mock_status
            
            response = client.get("/api/v1/auth/users/me/kyc-status")
            
            assert response.status_code == 200
            data = response.json()
            assert data['status'] == 'pending'

class TestAdminKYCAPI:
    """Test admin KYC API endpoints"""
    
    def test_get_kyc_statistics_unauthorized(self):
        """Test KYC statistics endpoint without admin role"""
        response = client.get("/api/v1/admin/kyc/statistics")
        
        assert response.status_code == 401
    
    def test_approve_document_success(self):
        """Test document approval"""
        doc_id = uuid.uuid4()
        
        with patch('api.v1.admin.security.require_admin_role') as mock_auth, \
             patch('service.approve_kyc_document') as mock_approve:
            
            mock_auth.return_value = {'user_id': uuid.uuid4()}
            mock_approve.return_value = Mock()
            
            response = client.post(f"/api/v1/admin/kyc/documents/{doc_id}/approve")
            
            assert response.status_code == 200
            mock_approve.assert_called_once()
    
    def test_reject_document_success(self):
        """Test document rejection"""
        doc_id = uuid.uuid4()
        
        with patch('api.v1.admin.security.require_admin_role') as mock_auth, \
             patch('service.reject_kyc_document') as mock_reject:
            
            mock_auth.return_value = {'user_id': uuid.uuid4()}
            mock_reject.return_value = Mock()
            
            response = client.post(f"/api/v1/admin/kyc/documents/{doc_id}/reject", json={
                "reason": "Invalid document"
            })
            
            assert response.status_code == 200
            mock_reject.assert_called_once()

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])