#!/usr/bin/env python
"""
Test script to verify the Field Services App setup.

This script checks:
1. Django installation
2. Database connectivity
3. App configurations
4. URL routing
"""

import os
import sys
import django
from pathlib import Path

# Add the project root directory to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

def check_django():
    """Check Django installation and configuration."""
    print("\n1. Checking Django installation...")
    try:
        print(f"Django version: {django.get_version()}")
        
        # Check Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        django.setup()
        
        from django.conf import settings
        print(f"DEBUG mode: {settings.DEBUG}")
        print(f"Database engine: {settings.DATABASES['default']['ENGINE']}")
        
        # Check installed apps
        print("\nRegistered Django apps:")
        for app in settings.INSTALLED_APPS:
            print(f"  - {app}")
        
        return True
    except Exception as e:
        print(f"Error checking Django: {e}")
        return False

def check_database_connection():
    """Verify database connection."""
    print("\n2. Testing database connection...")
    try:
        from django.db import connections
        connection = connections['default']
        connection.cursor()
        print("Database connection successful.")
        return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False

def check_models():
    """Check if models are properly registered."""
    print("\n3. Testing model registration...")
    try:
        # Check a few key models
        from django.apps import apps
        
        # Check User model
        User = apps.get_model("users", "User")
        print(f"User model: {User._meta.app_label}.{User._meta.model_name}")
        
        # List some fields from the User model
        print("User model fields:")
        for field in User._meta.fields[:5]:  # Show first 5 fields
            print(f"  - {field.name} ({field.get_internal_type()})")
            
        return True
    except Exception as e:
        print(f"Error checking models: {e}")
        return False

def check_urls():
    """Test URL configuration."""
    print("\n4. Testing URL configuration...")
    try:
        from django.urls import get_resolver
        resolver = get_resolver()
        
        # Print URL patterns (limited to first few to avoid overwhelming output)
        print("URL patterns:")
        patterns = resolver.url_patterns
        for i, pattern in enumerate(patterns[:10]):  # Show first 10 patterns
            print(f"  - {pattern.pattern}")
            
            # If it's an include pattern, show some nested patterns
            if hasattr(pattern, 'url_patterns'):
                for j, nested in enumerate(pattern.url_patterns[:3]):  # Show first 3 nested patterns
                    print(f"    - {nested.pattern}")
                if len(pattern.url_patterns) > 3:
                    print(f"    ... and {len(pattern.url_patterns) - 3} more")
                    
        return True
    except Exception as e:
        print(f"Error checking URLs: {e}")
        return False

def main():
    """Run all tests and report status."""
    print("=" * 80)
    print("Field Services App Setup Test")
    print("=" * 80)
    
    tests = [
        check_django,
        check_database_connection,
        check_models,
        check_urls,
    ]
    
    success = True
    for test in tests:
        if not test():
            success = False
    
    print("\n" + "=" * 80)
    if success:
        print("✅ All tests passed! The application is set up correctly.")
    else:
        print("❌ Some tests failed. Please fix the issues before continuing.")
    print("=" * 80)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
