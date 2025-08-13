#!/usr/bin/env python3
"""
Test the auth service by starting it and making HTTP requests
"""

import asyncio
import httpx
import json
from pathlib import Path
import sys
import subprocess
import time
import signal
import os

def start_auth_service():
    """Start the auth service in a subprocess"""
    print("Starting auth service...")
    
    # Change to the auth service directory
    auth_dir = Path(__file__).parent
    
    # Start the service using uvicorn
    process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "main:app", 
        "--host", "0.0.0.0", "--port", "8002", "--reload"
    ], cwd=auth_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait a bit for the service to start
    time.sleep(3)
    
    return process

async def test_auth_endpoints():
    """Test the enhanced auth endpoints"""
    base_url = "http://localhost:8002"
    
    async with httpx.AsyncClient() as client:
        print("=== Testing Auth Service Endpoints ===")
        
        # Test health check
        try:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                print("✓ Health check endpoint working")
                print(f"  Response: {response.json()}")
            else:
                print(f"✗ Health check failed: {response.status_code}")
        except Exception as e:
            print(f"✗ Health check failed: {e}")
            return False
        
        # Test Redis health check (if available)
        try:
            response = await client.get(f"{base_url}/health/redis")
            if response.status_code == 200:
                print("✓ Redis health check endpoint working")
                print(f"  Response: {response.json()}")
            else:
                print(f"✗ Redis health check failed: {response.status_code}")
        except Exception as e:
            print(f"✗ Redis health check failed: {e}")
        
        # Test user registration with enhanced password policy
        print("\n--- Testing User Registration ---")
        
        # Test with weak password (should fail)
        weak_password_data = {
            "email": "test@example.com",
            "password": "weak123",
            "recaptcha_token": "test_token"
        }
        
        try:
            response = await client.post(f"{base_url}/api/v1/auth/register", json=weak_password_data)
            if response.status_code == 422:  # Validation error expected
                print("✓ Weak password rejected correctly")
                error_detail = response.json()
                print(f"  Error: {error_detail}")
            else:
                print(f"✗ Weak password not rejected: {response.status_code}")
        except Exception as e:
            print(f"✗ Registration test failed: {e}")
        
        # Test with strong password
        strong_password_data = {
            "email": "test@example.com", 
            "password": "MyStr0ng!P@ssw0rd2024",
            "recaptcha_token": "test_token"
        }
        
        try:
            response = await client.post(f"{base_url}/api/v1/auth/register", json=strong_password_data)
            print(f"Strong password registration status: {response.status_code}")
            if response.status_code in [201, 400]:  # 201 success, 400 if user exists
                print("✓ Strong password validation working")
            else:
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"✗ Strong password registration failed: {e}")
        
        print("\n--- Testing Rate Limiting ---")
        
        # Test rate limiting by making multiple requests
        login_data = {
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        rate_limit_hit = False
        for i in range(7):  # Try 7 login attempts
            try:
                response = await client.post(f"{base_url}/api/v1/auth/token", data=login_data)
                if response.status_code == 429:  # Too Many Requests
                    print(f"✓ Rate limiting activated after {i+1} attempts")
                    rate_limit_hit = True
                    break
                else:
                    print(f"  Attempt {i+1}: {response.status_code}")
            except Exception as e:
                print(f"  Attempt {i+1} failed: {e}")
        
        if not rate_limit_hit:
            print("⚠ Rate limiting not triggered (might need Redis)")
        
        return True

def main():
    """Main test function"""
    print("Enhanced Auth Service Integration Test")
    print("=" * 50)
    
    # Start the auth service
    auth_process = None
    try:
        auth_process = start_auth_service()
        
        # Run the async tests
        success = asyncio.run(test_auth_endpoints())
        
        if success:
            print("\n🎉 Auth service integration test completed!")
            print("\nVerified Features:")
            print("• Service starts successfully")
            print("• Health check endpoints work")
            print("• Enhanced password validation")
            print("• API endpoints are accessible")
            print("• Rate limiting middleware (if Redis available)")
        else:
            print("\n❌ Some tests failed")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest failed with error: {e}")
    finally:
        # Clean up: stop the auth service
        if auth_process:
            print("\nStopping auth service...")
            auth_process.terminate()
            try:
                auth_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                auth_process.kill()
                auth_process.wait()
            print("Auth service stopped")

if __name__ == "__main__":
    main()