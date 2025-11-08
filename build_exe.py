"""
Build script for creating a standalone .exe using PyInstaller.
Run: python build_exe.py

This script uses the optimized FM26AttributeCustomizer.spec file
which excludes unused PyQt6 modules and unnecessary files to reduce size.
"""
import PyInstaller.__main__
import sys
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent

# Use the optimized spec file instead of command-line arguments
spec_file = project_root / 'FM26AttributeCustomizer.spec'

if not spec_file.exists():
    print(f"Error: Spec file not found: {spec_file}")
    sys.exit(1)

# PyInstaller arguments - use spec file for optimized build
args = [
    str(spec_file),
    '--clean',  # Clean PyInstaller cache before building
    '--noconfirm',  # Overwrite output directory without asking
]

print("Building optimized executable with PyInstaller...")
print(f"Using spec file: {spec_file}")
print("This build excludes unused PyQt6 modules to reduce file size.")
print()

# Run PyInstaller
PyInstaller.__main__.run(args)

print()
print("Build complete! Check the 'dist' folder for the executable.")
print("The optimized build should be significantly smaller than before.")

