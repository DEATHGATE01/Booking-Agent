#!/usr/bin/env python3
"""
Pre-deployment check script for TailorTalk assignment
"""
import os
import json
import sys
from pathlib import Path

def check_deployment_readiness():
    """Check if the project is ready for deployment"""
    print("🔍 TailorTalk Deployment Readiness Check\n")
    
    issues = []
    checks_passed = 0
    total_checks = 6
    
    # Check 1: Environment file
    if os.path.exists('.env'):
        print("✅ Environment file (.env) exists")
        checks_passed += 1
    else:
        print("❌ Environment file (.env) missing")
        issues.append("Create .env file with API keys")
    
    # Check 2: Service account file
    service_account_path = Path('credentials/service-account-key.json')
    if service_account_path.exists():
        print("✅ Google service account file exists")
        checks_passed += 1
        
        # Validate JSON
        try:
            with open(service_account_path) as f:
                data = json.load(f)
                if 'private_key' in data and 'client_email' in data:
                    print("  ✅ Service account file format is valid")
                else:
                    print("  ⚠️  Service account file may be incomplete")
        except:
            print("  ❌ Service account file is not valid JSON")
            issues.append("Fix service account JSON file")
    else:
        print("❌ Google service account file missing")
        issues.append("Add credentials/service-account-key.json")
    
    # Check 3: Backend requirements
    backend_req = Path('backend/requirements.txt')
    if backend_req.exists():
        print("✅ Backend requirements.txt exists")
        checks_passed += 1
    else:
        print("❌ Backend requirements.txt missing")
        issues.append("Create backend/requirements.txt")
    
    # Check 4: Frontend requirements  
    frontend_req = Path('frontend/requirements.txt')
    if frontend_req.exists():
        print("✅ Frontend requirements.txt exists")
        checks_passed += 1
    else:
        print("❌ Frontend requirements.txt missing")
        issues.append("Create frontend/requirements.txt")
    
    # Check 5: Railway configuration
    backend_railway = Path('backend/railway.toml')
    frontend_railway = Path('frontend/railway.toml')
    if backend_railway.exists() and frontend_railway.exists():
        print("✅ Railway configuration files exist")
        checks_passed += 1
    else:
        print("❌ Railway configuration incomplete")
        issues.append("Ensure railway.toml files exist")
    
    # Check 6: Git repository
    if os.path.exists('.git'):
        print("✅ Git repository initialized")
        checks_passed += 1
    else:
        print("❌ Git repository not found")
        issues.append("Initialize git repository and push to GitHub")
    
    print(f"\n📊 Readiness Score: {checks_passed}/{total_checks}")
    
    if checks_passed == total_checks:
        print("🎉 Project is ready for deployment!")
        print("\n🚀 Next steps:")
        print("1. Push latest changes to GitHub")
        print("2. Go to https://railway.app")
        print("3. Deploy backend first, then frontend")
        print("4. Test the deployed application")
        return True
    else:
        print("⚠️  Issues found that need attention:")
        for issue in issues:
            print(f"  - {issue}")
        return False

def show_environment_template():
    """Show template for environment variables"""
    print("\n📝 Environment Variables Template:")
    print("=" * 50)
    print("""
# Backend Environment Variables (Railway):
GOOGLE_CALENDAR_CREDENTIALS_PATH=credentials/service-account-key.json
GOOGLE_CALENDAR_ID=your-email@gmail.com
GEMINI_API_KEY=your-gemini-api-key
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False
TIMEZONE=UTC

# Frontend Environment Variables (Railway):
API_BASE_URL=https://your-backend-url.railway.app/api/v1
STREAMLIT_PORT=8501
""")

if __name__ == "__main__":
    if check_deployment_readiness():
        print("\n✅ Ready to deploy!")
    else:
        show_environment_template()
        print("\n🔧 Fix the issues above and run this script again.")
