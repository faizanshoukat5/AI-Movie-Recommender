#!/usr/bin/env python3
"""
Test script to verify all required endpoints are in the WSGI file
"""
import re

def test_wsgi_endpoints():
    """Test that all required endpoints are defined in wsgi_working.py"""
    
    # Required endpoints that the frontend expects
    required_endpoints = [
        '/models',
        '/movies',
        '/movies/random',
        '/search',
        '/recommendations/<int:user_id>',
        '/predict',
        '/compare/<int:user_id>',
        '/users/<int:user_id>/ratings',
        '/movies/<int:movie_id>/rate'
    ]
    
    # Read the WSGI file
    with open('wsgi_working.py', 'r') as f:
        content = f.read()
    
    # Find all @app.route definitions
    route_pattern = r"@app\.route\('([^']+)'"
    found_routes = re.findall(route_pattern, content)
    
    print("🧪 Testing WSGI file for required endpoints...")
    print("=" * 60)
    
    missing_endpoints = []
    
    for endpoint in required_endpoints:
        # Convert Flask route syntax to match patterns
        pattern = endpoint.replace('<int:user_id>', r'<int:\w+>')
        pattern = pattern.replace('<int:movie_id>', r'<int:\w+>')
        
        found = False
        for route in found_routes:
            if route == endpoint or re.match(pattern.replace('/', r'\/'), route):
                found = True
                break
        
        if found:
            print(f"✅ {endpoint}")
        else:
            print(f"❌ {endpoint}")
            missing_endpoints.append(endpoint)
    
    print("=" * 60)
    
    if missing_endpoints:
        print(f"❌ MISSING {len(missing_endpoints)} endpoints:")
        for endpoint in missing_endpoints:
            print(f"   - {endpoint}")
        print("\n🚨 Frontend will have errors!")
    else:
        print("✅ All required endpoints are present!")
        print("🎉 Frontend should work perfectly after deployment!")
    
    print(f"\nFound {len(found_routes)} total routes in WSGI file:")
    for route in found_routes:
        print(f"   - {route}")

if __name__ == "__main__":
    test_wsgi_endpoints()
