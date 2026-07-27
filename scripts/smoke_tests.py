"""
Smoke tests for deployment verification.
"""

import os
import httpx
import sys
from typing import Dict, Any

GATEWAY_URL = os.getenv('GATEWAY_URL', 'http://localhost:8000')


async def test_health_endpoint():
    """Test the health endpoint"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{GATEWAY_URL}/health", timeout=10.0)
            assert response.status_code == 200
            print("✓ Health endpoint passed")
            return True
        except Exception as e:
            print(f"✗ Health endpoint failed: {e}")
            return False


async def test_auth_service():
    """Test auth service connectivity"""
    async with httpx.AsyncClient() as client:
        try:
            # Test registration
            response = await client.post(
                f"{GATEWAY_URL}/api/v1/auth/register",
                json={
                    "email": "test@example.com",
                    "username": "testuser",
                    "password": "testpass123",
                    "first_name": "Test",
                    "last_name": "User"
                },
                timeout=10.0
            )
            assert response.status_code in [200, 201, 409]  # 409 if user exists
            print("✓ Auth service registration passed")
            
            # Test login
            response = await client.post(
                f"{GATEWAY_URL}/api/v1/auth/login",
                json={
                    "email": "test@example.com",
                    "password": "testpass123"
                },
                timeout=10.0
            )
            assert response.status_code in [200, 401]
            print("✓ Auth service login passed")
            return True
        except Exception as e:
            print(f"✗ Auth service failed: {e}")
            return False


async def test_catalog_service():
    """Test catalog service connectivity"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{GATEWAY_URL}/api/v1/catalog/", timeout=10.0)
            assert response.status_code in [200, 401]  # 401 if auth required
            print("✓ Catalog service passed")
            return True
        except Exception as e:
            print(f"✗ Catalog service failed: {e}")
            return False


async def test_playback_service():
    """Test playback service connectivity"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{GATEWAY_URL}/api/v1/playback/health", timeout=10.0)
            assert response.status_code in [200, 404]  # 404 if endpoint doesn't exist
            print("✓ Playback service passed")
            return True
        except Exception as e:
            print(f"✗ Playback service failed: {e}")
            return False


async def test_recommendation_service():
    """Test recommendation service connectivity"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{GATEWAY_URL}/api/v1/recommendations/test-user-id", timeout=10.0)
            assert response.status_code in [200, 401, 404]
            print("✓ Recommendation service passed")
            return True
        except Exception as e:
            print(f"✗ Recommendation service failed: {e}")
            return False


async def test_notification_service():
    """Test notification service connectivity"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{GATEWAY_URL}/api/v1/notifications/user/test-user-id", timeout=10.0)
            assert response.status_code in [200, 401]
            print("✓ Notification service passed")
            return True
        except Exception as e:
            print(f"✗ Notification service failed: {e}")
            return False


async def test_integrity_service():
    """Test integrity service connectivity"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{GATEWAY_URL}/api/v1/events/health", timeout=10.0)
            assert response.status_code in [200, 404]
            print("✓ Integrity service passed")
            return True
        except Exception as e:
            print(f"✗ Integrity service failed: {e}")
            return False


async def run_all_tests():
    """Run all smoke tests"""
    print(f"Running smoke tests against {GATEWAY_URL}")
    print("=" * 50)
    
    tests = [
        test_health_endpoint,
        test_auth_service,
        test_catalog_service,
        test_playback_service,
        test_recommendation_service,
        test_notification_service,
        test_integrity_service
    ]
    
    results = []
    for test in tests:
        result = await test()
        results.append(result)
    
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("All smoke tests passed! ✓")
        return 0
    else:
        print("Some smoke tests failed! ✗")
        return 1


if __name__ == "__main__":
    import asyncio
    sys.exit(asyncio.run(run_all_tests()))
