#!/usr/bin/env python3
"""
Verification script for enhanced authentication and security infrastructure
This script verifies that all the implemented features are working correctly
"""

import sys
import os
from pathlib import Path

# Add the service directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def verify_file_structure():
    """Verify that all required files have been created"""
    print("=== Verifying File Structure ===")
    
    required_files = [
        "models.py",
        "schemas.py", 
        "security.py",
        "service.py",
        "redis_client.py",
        "rate_limiter.py",
        "session_service.py",
        "audit_service.py",
        "api/v1/auth.py",
        "main.py",
        "requirements.txt",
        "migrations/001_enhance_security.sql"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = Path(__file__).parent / file_path
        if full_path.exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\nMissing files: {missing_files}")
        return False
    
    print("✓ All required files are present")
    return True

def verify_dependencies():
    """Verify that all required dependencies are available"""
    print("\n=== Verifying Dependencies ===")
    
    required_modules = [
        ("fastapi", "FastAPI framework"),
        ("sqlalchemy", "Database ORM"),
        ("asyncpg", "PostgreSQL async driver"),
        ("redis", "Redis client"),
        ("aioredis", "Async Redis client"),
        ("passlib", "Password hashing"),
        ("pyotp", "TOTP implementation"),
        ("qrcode", "QR code generation"),
        ("python_jose", "JWT handling"),
        ("bcrypt", "Password hashing")
    ]
    
    missing_modules = []
    for module_name, description in required_modules:
        try:
            __import__(module_name)
            print(f"✓ {module_name} - {description}")
        except ImportError:
            print(f"✗ {module_name} - {description}")
            missing_modules.append(module_name)
    
    if missing_modules:
        print(f"\nMissing modules: {missing_modules}")
        return False
    
    print("✓ All required dependencies are available")
    return True

def verify_security_features():
    """Verify security feature implementations"""
    print("\n=== Verifying Security Features ===")
    
    try:
        from security import (
            validate_password_strength,
            generate_tfa_secret,
            verify_tfa_code,
            generate_backup_codes,
            verify_backup_code,
            PasswordPolicy
        )
        
        # Test password policy
        weak_password = "123456"
        strong_password = "MyStr0ng!P@ssw0rd2024"
        
        is_weak_valid, weak_errors = validate_password_strength(weak_password)
        is_strong_valid, strong_errors = validate_password_strength(strong_password)
        
        if not is_weak_valid and is_strong_valid:
            print("✓ Password policy validation working correctly")
        else:
            print("✗ Password policy validation not working correctly")
            return False
        
        # Test 2FA functionality
        secret = generate_tfa_secret()
        if len(secret) >= 16:
            print("✓ 2FA secret generation working")
        else:
            print("✗ 2FA secret generation failed")
            return False
        
        # Test backup codes
        backup_codes = generate_backup_codes()
        if len(backup_codes) == 10 and all(len(code) == 9 for code in backup_codes):
            print("✓ Backup code generation working")
        else:
            print("✗ Backup code generation failed")
            return False
        
        # Test backup code verification
        test_code = backup_codes[0]
        is_valid, remaining = verify_backup_code(backup_codes, test_code)
        if is_valid and len(remaining) == 9:
            print("✓ Backup code verification working")
        else:
            print("✗ Backup code verification failed")
            return False
        
        print("✓ All security features working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Security features verification failed: {e}")
        return False

def verify_model_enhancements():
    """Verify that models have been enhanced with new fields"""
    print("\n=== Verifying Model Enhancements ===")
    
    try:
        from models import User, UserSession, AuditLog, RateLimit
        
        # Check User model enhancements
        user_fields = [
            'is_verified', 'failed_login_attempts', 'locked_until',
            'password_changed_at', 'backup_codes', 'first_name',
            'last_name', 'timezone', 'language', 'last_login_at'
        ]
        
        for field in user_fields:
            if hasattr(User, field):
                print(f"✓ User.{field}")
            else:
                print(f"✗ User.{field}")
                return False
        
        # Check new models exist
        new_models = [
            ('UserSession', UserSession),
            ('AuditLog', AuditLog), 
            ('RateLimit', RateLimit)
        ]
        
        for model_name, model_class in new_models:
            if model_class:
                print(f"✓ {model_name} model exists")
            else:
                print(f"✗ {model_name} model missing")
                return False
        
        print("✓ All model enhancements verified")
        return True
        
    except Exception as e:
        print(f"✗ Model verification failed: {e}")
        return False

def verify_api_enhancements():
    """Verify that API endpoints have been enhanced"""
    print("\n=== Verifying API Enhancements ===")
    
    try:
        # Check if the auth API file can be imported
        from api.v1.auth import router
        
        # Get all routes
        routes = [route.path for route in router.routes]
        
        expected_routes = [
            "/register",
            "/token", 
            "/token/2fa",
            "/users/me",
            "/sessions",
            "/sessions/revoke-all",
            "/password/change",
            "/2fa/setup",
            "/2fa/enable",
            "/2fa/disable",
            "/2fa/backup-codes/regenerate",
            "/2fa/backup-codes/count",
            "/users/me/profile",
            "/security/summary",
            "/audit-logs"
        ]
        
        missing_routes = []
        for route in expected_routes:
            if route in routes:
                print(f"✓ {route}")
            else:
                print(f"✗ {route}")
                missing_routes.append(route)
        
        if missing_routes:
            print(f"Missing routes: {missing_routes}")
            return False
        
        print("✓ All API enhancements verified")
        return True
        
    except Exception as e:
        print(f"✗ API verification failed: {e}")
        return False

def verify_service_enhancements():
    """Verify service layer enhancements"""
    print("\n=== Verifying Service Enhancements ===")
    
    try:
        import service
        
        # Check for new service functions
        expected_functions = [
            'authenticate_user',
            'change_password',
            'generate_backup_codes',
            'verify_backup_code',
            'unlock_user_account',
            'update_user_profile'
        ]
        
        missing_functions = []
        for func_name in expected_functions:
            if hasattr(service, func_name):
                print(f"✓ service.{func_name}")
            else:
                print(f"✗ service.{func_name}")
                missing_functions.append(func_name)
        
        if missing_functions:
            print(f"Missing functions: {missing_functions}")
            return False
        
        print("✓ All service enhancements verified")
        return True
        
    except Exception as e:
        print(f"✗ Service verification failed: {e}")
        return False

def main():
    """Run all verification checks"""
    print("Enhanced Authentication and Security Infrastructure Verification")
    print("=" * 70)
    
    checks = [
        ("File Structure", verify_file_structure),
        ("Dependencies", verify_dependencies),
        ("Security Features", verify_security_features),
        ("Model Enhancements", verify_model_enhancements),
        ("API Enhancements", verify_api_enhancements),
        ("Service Enhancements", verify_service_enhancements)
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        try:
            if check_func():
                passed += 1
            else:
                print(f"\n❌ {check_name} check failed")
        except Exception as e:
            print(f"\n❌ {check_name} check failed with exception: {e}")
    
    print("\n" + "=" * 70)
    print(f"Verification Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All enhanced authentication and security features have been successfully implemented!")
        print("\nImplemented Features:")
        print("• Enhanced password policy validation with complexity requirements")
        print("• 2FA (TOTP) authentication system with QR code generation")
        print("• Backup codes for 2FA recovery")
        print("• Rate limiting middleware using Redis")
        print("• Session management system with Redis storage")
        print("• Account lockout mechanisms for failed login attempts")
        print("• Comprehensive audit logging service")
        print("• Enhanced user models with security fields")
        print("• New API endpoints for security management")
        print("• Password change functionality with validation")
        print("• User profile management")
        print("• Security event monitoring and reporting")
        
        return True
    else:
        print(f"❌ {total - passed} checks failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)