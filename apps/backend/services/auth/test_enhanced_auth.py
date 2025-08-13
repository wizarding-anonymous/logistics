#!/usr/bin/env python3
"""
Test script for enhanced authentication features
"""

import asyncio
import sys
from pathlib import Path

# Add the service directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from security import (
        validate_password_strength, 
        generate_tfa_secret, 
        verify_tfa_code, 
        generate_backup_codes, 
        verify_backup_code
    )
    print("✓ Security module imported successfully")
except ImportError as e:
    print(f"✗ Failed to import security module: {e}")
    sys.exit(1)

def test_password_validation():
    """Test password policy validation"""
    print("=== Testing Password Validation ===")
    
    # Test weak passwords
    weak_passwords = [
        "123456",
        "password",
        "Password1",
        "Password123",
        "VeryLongPasswordWithoutSpecialChars123"
    ]
    
    for password in weak_passwords:
        is_valid, errors = validate_password_strength(password)
        print(f"Password: '{password}' - Valid: {is_valid}")
        if not is_valid:
            print(f"  Errors: {errors}")
    
    # Test strong password
    strong_password = "MyStr0ng!P@ssw0rd2024"
    is_valid, errors = validate_password_strength(strong_password)
    print(f"Strong password: '{strong_password}' - Valid: {is_valid}")
    if not is_valid:
        print(f"  Errors: {errors}")

def test_2fa_functionality():
    """Test 2FA TOTP functionality"""
    print("\n=== Testing 2FA Functionality ===")
    
    # Generate secret
    secret = generate_tfa_secret()
    print(f"Generated secret: {secret}")
    
    # Generate backup codes
    backup_codes = generate_backup_codes()
    print(f"Generated {len(backup_codes)} backup codes: {backup_codes[:3]}...")
    
    # Test backup code verification
    test_code = backup_codes[0]
    is_valid, remaining = verify_backup_code(backup_codes, test_code)
    print(f"Backup code '{test_code}' valid: {is_valid}")
    print(f"Remaining codes: {len(remaining)}")
    
    # Test invalid backup code
    is_valid, remaining = verify_backup_code(remaining, "INVALID-CODE")
    print(f"Invalid backup code valid: {is_valid}")

async def test_redis_functionality():
    """Test Redis functionality"""
    print("\n=== Testing Redis Functionality ===")
    print("Note: Skipping Redis tests as they require Redis server and proper module imports")

async def test_rate_limiter():
    """Test rate limiter functionality"""
    print("\n=== Testing Rate Limiter ===")
    print("Note: Skipping rate limiter tests as they require Redis server and proper module imports")

async def main():
    """Run all tests"""
    print("Enhanced Authentication Features Test")
    print("=" * 50)
    
    # Test password validation (no async needed)
    test_password_validation()
    
    # Test 2FA functionality (no async needed)
    test_2fa_functionality()
    
    # Test Redis functionality (requires Redis)
    await test_redis_functionality()
    
    # Test rate limiter (requires Redis)
    await test_rate_limiter()
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    asyncio.run(main())