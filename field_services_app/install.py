#!/usr/bin/env python
"""
Installation script for the Field Services Application.
This script checks the environment, installs requirements, and sets up the initial project structure.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def print_step(message):
    """Print a formatted step message."""
    print("\n" + "=" * 80)
    print(f"  {message}")
    print("=" * 80)

def run_command(command, description):
    """Run a shell command with error handling."""
    print_step(description)
    print(f"Running: {' '.join(command)}")
    
    try:
        process = subprocess.run(command, check=True, capture_output=True, text=True)
        print(process.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"Command output: {e.stdout}")
        print(f"Command error: {e.stderr}")
        return False

def check_python_version():
    """Check if the Python version is compatible."""
    print_step("Checking Python version")
    version = sys.version_info
    required_version = (3, 8)
    
    if version < required_version:
        print(f"Python {required_version[0]}.{required_version[1]} or higher is required.")
        print(f"You are using Python {version[0]}.{version[1]}.{version[2]}")
        return False
    
    print(f"Using Python {version[0]}.{version[1]}.{version[2]} ✓")
    return True

def check_virtual_environment():
    """Check if running in a virtual environment."""
    print_step("Checking virtual environment")
    
    if sys.prefix == sys.base_prefix:
        print("Warning: Not running in a virtual environment.")
        print("It's recommended to install the project in a virtual environment.")
        
        if input("Would you like to continue anyway? (y/n): ").lower() != 'y':
            print("Installation aborted. Please create and activate a virtual environment first.")
            print("Example:")
            print("  python -m venv venv")
            if platform.system() == "Windows":
                print("  venv\\Scripts\\activate")
            else:
                print("  source venv/bin/activate")
            return False
    else:
        print(f"Virtual environment detected: {sys.prefix} ✓")
    
    return True

def install_requirements():
    """Install project requirements."""
    print_step("Installing requirements")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print(f"Error: {requirements_file} not found.")
        return False
    
    return run_command([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
                       "Installing requirements from requirements.txt")

def install_package():
    """Install the package in development mode."""
    print_step("Installing package in development mode")
    
    return run_command([sys.executable, "-m", "pip", "install", "-e", "."],
                      "Installing package in development mode")

def create_env_file():
    """Create a .env file if it doesn't exist."""
    print_step("Creating .env file")
    
    env_file = Path(".env")
    if env_file.exists():
        print(".env file already exists. Skipping.")
        return True
    
    import secrets
    secret_key = secrets.token_urlsafe(32)
    
    with open(env_file, "w") as f:
        f.write(f"DEBUG=True\n")
        f.write(f"SECRET_KEY={secret_key}\n")
        f.write(f"ALLOWED_HOSTS=localhost,127.0.0.1\n")
        f.write(f"DATABASE_URL=sqlite:///db.sqlite3\n")
    
    print(".env file created with default values ✓")
    return True

def check_django_installation():
    """Check if Django is properly installed."""
    print_step("Checking Django installation")
    
    check_script = Path("check_django.py")
    if not check_script.exists():
        print(f"Error: {check_script} not found.")
        return False
    
    return run_command([sys.executable, str(check_script)],
                       "Running Django check script")

def create_directories():
    """Create necessary directories if they don't exist."""
    print_step("Creating directories")
    
    directories = [
        "static",
        "templates",
        "media",
        "logs",
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Directory '{directory}' created/checked ✓")
    
    return True

def main():
    """Main installation function."""
    print("\nField Services Application Installation\n")
    
    # Change to the project directory
    project_dir = Path(__file__).resolve().parent
    os.chdir(project_dir)
    print(f"Working directory: {os.getcwd()}")
    
    # Run installation steps
    steps = [
        check_python_version,
        check_virtual_environment,
        install_requirements,
        install_package,
        create_env_file,
        create_directories,
        check_django_installation,
    ]
    
    success = True
    for step in steps:
        if not step():
            success = False
            break
    
    if success:
        print("\n" + "=" * 80)
        print("  Installation completed successfully!")
        print("=" * 80)
        print("\nNext steps:")
        print("1. Run migrations:    python manage.py migrate")
        print("2. Create superuser:  python manage.py createsuperuser")
        print("3. Start the server:  python manage.py runserver")
        return 0
    else:
        print("\n" + "=" * 80)
        print("  Installation failed. Please fix the issues and try again.")
        print("=" * 80)
        return 1

if __name__ == "__main__":
    sys.exit(main())
