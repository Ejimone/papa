#!/usr/bin/env python3
import sys
import os

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    import app.main
    print("✅ Successfully imported app.main")
    
    # Test a simple HTTP request
    from fastapi.testclient import TestClient
    client = TestClient(app.main.app)
    response = client.get("/")
    print(f"✅ Root endpoint status: {response.status_code}")
    print(f"✅ Response: {response.json()}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
