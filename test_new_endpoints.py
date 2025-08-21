#!/usr/bin/env python3
"""
Simple test script to validate the new separated CRUD endpoints
"""
import requests
import json
import sys

# Base URL for the API
BASE_URL = "http://127.0.0.1:5000"

def test_endpoint(method, endpoint, description, data=None, headers=None):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n🧪 Testing: {method} {endpoint}")
    print(f"📝 Description: {description}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=5)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=5)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=5)
        elif method == "PATCH":
            response = requests.patch(url, json=data, headers=headers, timeout=5)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
        
        print(f"📊 Status Code: {response.status_code}")
        
        # Check if it's a JSON response
        try:
            response_json = response.json()
            if response.status_code == 401:
                print("🔒 Expected: Requires authentication (401)")
                return True
            elif response.status_code == 403:
                print("🔒 Expected: Requires admin role (403)")
                return True
            elif response.status_code < 500:
                print("✅ Endpoint is accessible")
                return True
            else:
                print(f"❌ Server error: {response.status_code}")
                return False
        except:
            print(f"❌ Non-JSON response or server error")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False

def main():
    print("🚀 Testing New Separated CRUD Endpoints")
    print("=" * 50)
    
    success_count = 0
    total_count = 0
    
    # Test student endpoints
    student_endpoints = [
        ("GET", "/api/admin/students", "List all students (Admin only)"),
        ("POST", "/api/admin/students", "Create new student (Admin only)"),
        ("GET", "/api/admin/students/test_id", "Get student details (Admin only)"),
        ("PUT", "/api/admin/students/test_id", "Update student (Admin only)"),
        ("DELETE", "/api/admin/students/test_id", "Delete student (Admin only)"),
        ("PATCH", "/api/admin/students/test_id/verify", "Verify student (Admin only)"),
        ("PATCH", "/api/admin/students/test_id/block", "Block student (Admin only)"),
    ]
    
    # Test teacher endpoints
    teacher_endpoints = [
        ("GET", "/api/admin/teachers", "List all teachers (Admin only)"),
        ("POST", "/api/admin/teachers", "Create new teacher (Admin only)"),
        ("GET", "/api/admin/teachers/test_id", "Get teacher details (Admin only)"),
        ("PUT", "/api/admin/teachers/test_id", "Update teacher (Admin only)"),
        ("DELETE", "/api/admin/teachers/test_id", "Delete teacher (Admin only)"),
        ("PATCH", "/api/admin/teachers/test_id/verify", "Verify teacher (Admin only)"),
        ("PATCH", "/api/admin/teachers/test_id/block", "Block teacher (Admin only)"),
    ]
    
    # Test teacher assignment endpoints
    assignment_endpoints = [
        ("GET", "/api/admin/teachers/test_id/students", "Get teacher's students (Admin only)"),
        ("POST", "/api/admin/teachers/test_id/students", "Assign students to teacher (Admin only)"),
        ("DELETE", "/api/admin/teachers/test_id/students/student_id", "Unassign student from teacher (Admin only)"),
    ]
    
    # Test modified user endpoint
    user_endpoints = [
        ("GET", "/api/admin/users", "List all users (Admin only)"),
    ]
    
    all_endpoints = [
        ("Student Management", student_endpoints),
        ("Teacher Management", teacher_endpoints), 
        ("Teacher Assignments", assignment_endpoints),
        ("User Listing", user_endpoints)
    ]
    
    for section_name, endpoints in all_endpoints:
        print(f"\n📋 {section_name}")
        print("-" * 30)
        
        for method, endpoint, description in endpoints:
            if test_endpoint(method, endpoint, description):
                success_count += 1
            total_count += 1
    
    print(f"\n📊 Test Results")
    print("=" * 50)
    print(f"✅ Successful: {success_count}/{total_count}")
    print(f"❌ Failed: {total_count - success_count}/{total_count}")
    
    if success_count == total_count:
        print("\n🎉 All endpoints are properly configured!")
        print("💡 Note: 401/403 responses are expected for admin endpoints without authentication")
    else:
        print(f"\n⚠️  Some endpoints may need attention")
        
    # Test that OpenAPI spec includes the new endpoints
    print(f"\n🔍 Checking OpenAPI Specification")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/apispec_1.json", timeout=5)
        if response.status_code == 200:
            spec = response.json()
            paths = spec.get('paths', {})
            
            # Check for new student endpoints
            student_paths = [p for p in paths.keys() if '/api/admin/students' in p]
            teacher_paths = [p for p in paths.keys() if '/api/admin/teachers' in p]
            user_paths = [p for p in paths.keys() if '/api/admin/users' in p]
            
            print(f"📊 Student endpoints in spec: {len(student_paths)}")
            print(f"📊 Teacher endpoints in spec: {len(teacher_paths)}")
            print(f"📊 User endpoints in spec: {len(user_paths)}")
            
            if student_paths and teacher_paths:
                print("✅ New endpoints are documented in OpenAPI spec")
            else:
                print("❌ New endpoints missing from OpenAPI spec")
                
        else:
            print(f"❌ Failed to get OpenAPI spec: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking OpenAPI spec: {e}")

if __name__ == "__main__":
    main()