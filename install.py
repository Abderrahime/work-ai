#!/usr/bin/env python3
"""
FreeWork Job Application Assistant - Installation Script
"""

import sys
import subprocess
import os
import platform
import venv

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def create_virtual_environment():
    """Create a virtual environment for the project"""
    venv_path = "venv"
    
    if os.path.exists(venv_path):
        print(f"✅ Virtual environment already exists at {venv_path}")
        return venv_path
    
    print("📦 Creating virtual environment...")
    try:
        venv.create(venv_path, with_pip=True)
        print(f"✅ Virtual environment created at {venv_path}")
        return venv_path
    except Exception as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return None

def get_python_executable(venv_path):
    """Get the Python executable path for the virtual environment"""
    if platform.system().lower() == "windows":
        return os.path.join(venv_path, "Scripts", "python.exe")
    else:
        return os.path.join(venv_path, "bin", "python")

def get_pip_executable(venv_path):
    """Get the pip executable path for the virtual environment"""
    if platform.system().lower() == "windows":
        return os.path.join(venv_path, "Scripts", "pip.exe")
    else:
        return os.path.join(venv_path, "bin", "pip")

def install_package(pip_executable, package):
    """Install a Python package using the virtual environment pip"""
    try:
        subprocess.check_call([pip_executable, "install", package])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing {package}: {e}")
        return False

def check_firefox():
    """Check if Firefox is installed"""
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        firefox_paths = [
            "/Applications/Firefox.app",
            "/usr/bin/firefox",
            "/usr/local/bin/firefox"
        ]
    elif system == "linux":
        firefox_paths = [
            "/usr/bin/firefox",
            "/usr/local/bin/firefox",
            "/snap/bin/firefox"
        ]
    elif system == "windows":
        firefox_paths = [
            "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
            "C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe"
        ]
    else:
        print("⚠️  Unknown operating system")
        return False
    
    for path in firefox_paths:
        if os.path.exists(path):
            print("✅ Firefox found")
            return True
    
    print("❌ Firefox not found")
    print("Please install Firefox from: https://www.mozilla.org/firefox/")
    return False

def check_geckodriver():
    """Check if geckodriver is installed"""
    try:
        result = subprocess.run(['geckodriver', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ geckodriver found")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ geckodriver not found")
    return False

def install_geckodriver():
    """Install geckodriver"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    print("📥 Installing geckodriver...")
    
    if system == "darwin":  # macOS
        try:
            subprocess.check_call(['brew', 'install', 'geckodriver'])
            print("✅ geckodriver installed via Homebrew")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Homebrew not found or installation failed")
            print("Please install manually: https://github.com/mozilla/geckodriver/releases")
            return False
    
    elif system == "linux":
        try:
            subprocess.check_call(['sudo', 'apt-get', 'update'])
            subprocess.check_call(['sudo', 'apt-get', 'install', '-y', 'firefox-geckodriver'])
            print("✅ geckodriver installed via apt")
            return True
        except subprocess.CalledProcessError:
            print("❌ apt installation failed")
            print("Please install manually: https://github.com/mozilla/geckodriver/releases")
            return False
    
    else:
        print("⚠️  Please install geckodriver manually")
        print("Download from: https://github.com/mozilla/geckodriver/releases")
        return False

def install_dependencies(pip_executable):
    """Install Python dependencies"""
    print("📥 Installing Python dependencies...")
    
    dependencies = [
        'selenium==4.15.2',
        'cryptography==41.0.7'
    ]
    
    for dep in dependencies:
        print(f"Installing {dep}...")
        if install_package(pip_executable, dep):
            print(f"✅ {dep} installed")
        else:
            print(f"❌ Failed to install {dep}")
            return False
    
    return True

def create_run_script(venv_path):
    """Create a run script for easy execution"""
    python_executable = get_python_executable(venv_path)
    
    if platform.system().lower() == "windows":
        script_content = f"""@echo off
echo Starting FreeWork Job Application Assistant...
"{python_executable}" main.py
pause
"""
        script_path = "run.bat"
    else:
        script_content = f"""#!/bin/bash
echo "Starting FreeWork Job Application Assistant..."
"{python_executable}" main.py
"""
        script_path = "run.sh"
    
    # Create the script file
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Set executable permissions for Unix-like systems
    if platform.system().lower() != "windows":
        try:
            os.chmod(script_path, 0o755)
        except Exception as e:
            print(f"Warning: Could not set executable permissions on {script_path}: {e}")
    
    print(f"✅ Created run script: {script_path}")

def main():
    """Main installation function"""
    print("🚀 FreeWork Job Application Assistant - Installation")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check Firefox
    if not check_firefox():
        print("\nPlease install Firefox and run this script again.")
        sys.exit(1)
    
    # Check geckodriver
    if not check_geckodriver():
        print("\nInstalling geckodriver...")
        if not install_geckodriver():
            sys.exit(1)
    
    # Create virtual environment
    venv_path = create_virtual_environment()
    if not venv_path:
        sys.exit(1)
    
    # Get pip executable
    pip_executable = get_pip_executable(venv_path)
    
    # Install Python dependencies
    if not install_dependencies(pip_executable):
        print("\nFailed to install Python dependencies.")
        sys.exit(1)
    
    # Create run script
    create_run_script(venv_path)
    
    print("\n" + "=" * 50)
    print("✅ Installation completed successfully!")
    print("\n🎯 Next steps:")
    print("1. Run the application using one of these methods:")
    print("   • Double-click: run.sh (macOS/Linux) or run.bat (Windows)")
    print("   • Command line: source venv/bin/activate && python main.py")
    print("   • Direct: ./venv/bin/python main.py")
    print("2. Configure your credentials and search parameters")
    print("3. Start your first application session!")
    print("\n📚 For more information, see README.md")
    print("\n💡 Note: The virtual environment isolates this application's dependencies")
    print("   from your system Python installation.")

if __name__ == "__main__":
    main() 