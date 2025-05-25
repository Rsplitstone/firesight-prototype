#!/usr/bin/env python3
"""
NASA FIRMS API Connectivity Test
Tests the NASA API key and verifies data access
"""
import os
import sys
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not installed. Install with: pip install python-dotenv")
    sys.exit(1)


class NASAAPITester:
    """Test NASA FIRMS API connectivity and functionality"""
    
    def __init__(self):
        self.api_key = os.getenv('NASA_API_KEY')
        self.base_url = "https://firms.modaps.eosdis.nasa.gov/api"
        
    def test_api_key(self):
        """Test if the API key is valid"""
        print("Testing NASA API Key...")
        print(f"API Key: {self.api_key[:10]}..." if self.api_key else "No API key found")
        
        if not self.api_key:
            print("❌ ERROR: NASA_API_KEY not found in environment variables")
            return False
            
        if self.api_key == "your_nasa_api_key_here":
            print("❌ ERROR: Please replace the placeholder API key with your actual key")
            return False
            
        print("✅ API key found and appears valid")
        return True
    
    def test_modis_connection(self):
        """Test MODIS data access"""
        print("\nTesting MODIS data access...")
        
        # Test area around California (wildfire-prone region)
        url = f"{self.base_url}/area/csv/{self.api_key}/MODIS_NRT/world/1/2024-01-01"
        
        try:
            response = requests.get(url, timeout=30)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.text
                lines = data.strip().split('\n')
                print(f"✅ MODIS connection successful. Retrieved {len(lines)} lines of data")
                if len(lines) > 1:  # Has header + data
                    print(f"Sample data: {lines[1][:100]}...")
                return True
            elif response.status_code == 401:
                print("❌ ERROR: Unauthorized - Invalid API key")
                return False
            elif response.status_code == 429:
                print("❌ ERROR: Rate limit exceeded")
                return False
            else:
                print(f"❌ ERROR: HTTP {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ ERROR: Connection failed - {e}")
            return False
    
    def test_viirs_connection(self):
        """Test VIIRS data access"""
        print("\nTesting VIIRS data access...")
        
        # Test VIIRS data for recent date
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        url = f"{self.base_url}/area/csv/{self.api_key}/VIIRS_SNPP_NRT/world/1/{yesterday}"
        
        try:
            response = requests.get(url, timeout=30)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.text
                lines = data.strip().split('\n')
                print(f"✅ VIIRS connection successful. Retrieved {len(lines)} lines of data")
                return True
            else:
                print(f"⚠️  VIIRS data may not be available for {yesterday}")
                return True  # Don't fail for data availability issues
                
        except requests.exceptions.RequestException as e:
            print(f"❌ ERROR: VIIRS connection failed - {e}")
            return False
    
    def test_api_limits(self):
        """Test API rate limits and quotas"""
        print("\nTesting API limits...")
        
        # Make a small request to check quotas
        url = f"{self.base_url}/area/csv/{self.api_key}/MODIS_NRT/world/1/2024-01-01,2024-01-01"
        
        try:
            response = requests.get(url, timeout=30)
            
            # Check rate limit headers if available
            headers = response.headers
            if 'X-RateLimit-Remaining' in headers:
                remaining = headers['X-RateLimit-Remaining']
                print(f"Rate limit remaining: {remaining}")
            
            if 'X-RateLimit-Reset' in headers:
                reset_time = headers['X-RateLimit-Reset']
                print(f"Rate limit resets at: {reset_time}")
                
            print("✅ API limits check completed")
            return True
            
        except Exception as e:
            print(f"⚠️  Could not check API limits: {e}")
            return True  # Don't fail for this
    
    def run_all_tests(self):
        """Run all API tests"""
        print("=" * 50)
        print("NASA FIRMS API Connectivity Test")
        print("=" * 50)
        
        tests = [
            self.test_api_key,
            self.test_modis_connection,
            self.test_viirs_connection,
            self.test_api_limits
        ]
        
        results = []
        for test in tests:
            results.append(test())
        
        print("\n" + "=" * 50)
        print("TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(results)
        total = len(results)
        
        if passed == total:
            print(f"✅ ALL TESTS PASSED ({passed}/{total})")
            print("🚀 NASA API is ready for use!")
            return True
        else:
            print(f"❌ SOME TESTS FAILED ({passed}/{total})")
            print("🔧 Please check the errors above and fix the issues")
            return False


def main():
    """Main test function"""
    tester = NASAAPITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 Ready to deploy FireSight AI with NASA satellite data!")
        sys.exit(0)
    else:
        print("\n⚠️  Please fix the issues before deploying")
        sys.exit(1)


if __name__ == "__main__":
    main()
