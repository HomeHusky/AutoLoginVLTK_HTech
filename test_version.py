"""Test script để kiểm tra version manager"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from modules.version_manager import version_manager

# Test get version
print("Testing version manager...")
print(f"Version file path: {version_manager.version_file}")
print(f"File exists: {os.path.exists(version_manager.version_file)}")

version = version_manager.get_current_version()
print(f"Current version: {version}")

if version:
    print("✅ Version manager works!")
else:
    print("❌ Version manager failed!")
