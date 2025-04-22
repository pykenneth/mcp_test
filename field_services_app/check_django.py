#!/usr/bin/env python
"""
Simple script to check if Django is installed and accessible.
"""

import sys

def check_django():
    try:
        import django
        print(f"Django is installed. Version: {django.get_version()}")
        
        # Check additional packages
        try:
            import rest_framework
            print(f"Django REST Framework is installed.")
        except ImportError:
            print("Django REST Framework is not installed.")
        
        try:
            import drf_yasg
            print(f"DRF YASG is installed.")
        except ImportError:
            print("DRF YASG is not installed.")
            
        print("\nDjango installation path:")
        print(django.__path__)
        return True
    except ImportError:
        print("Django is not installed or not accessible in your Python environment.")
        print("\nTroubleshooting tips:")
        print("1. Make sure you have activated your virtual environment (if using one)")
        print("2. Install Django using: pip install -r requirements.txt")
        print("3. Check your PYTHONPATH environment variable")
        return False

if __name__ == "__main__":
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print("Checking Django installation...\n")
    
    success = check_django()
    
    if success:
        print("\nYour Django environment appears to be set up correctly.")
    else:
        print("\nUnable to import Django. Please fix the issues before continuing.")
        sys.exit(1)
