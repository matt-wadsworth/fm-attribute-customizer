# Building FM26 Attribute Customizer

This guide explains how to build a standalone executable (.exe) for Windows distribution.

## Prerequisites

1. **Python 3.8 or higher** installed
2. **All dependencies** installed:
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

## Adding an Icon (Optional)

1. Create or obtain an icon file:
   - **Windows**: `.ico` file (recommended: 256x256 or 128x128 pixels)
   - **Alternative**: `.png` file` (will be converted)

2. Place the icon file in the project root:
   - `icon.ico` (preferred)
   - OR `icon.png` (fallback)

3. The application will automatically use the icon if found.

## Building the Executable

### Option 1: Using the Build Script (Recommended)

Simply run:
```bash
python build_exe.py
```

This will create a single-file executable in the `dist` folder.

### Option 2: Using PyInstaller Directly

```bash
pyinstaller --name=FM26AttributeCustomizer --onefile --windowed --icon=icon.ico main.py
```

### Build Options Explained

- `--onefile`: Creates a single executable file (easier to distribute)
- `--windowed`: No console window (GUI app only)
- `--icon=icon.ico`: Sets the application icon
- `--clean`: Cleans cache before building
- `--noconfirm`: Overwrites output without asking

## Output

After building, you'll find:
- **Executable**: `dist/FM26AttributeCustomizer.exe` (or `FM26AttributeCustomizer` on Linux/Mac)
- **Build files**: `build/` folder (can be deleted)
- **Spec file**: `FM26AttributeCustomizer.spec` (can be kept for custom builds)

## Distribution

1. Test the executable on a clean machine (without Python installed)
2. The executable is self-contained and includes all dependencies
3. Users don't need Python or any dependencies installed
4. The executable may be flagged by antivirus software (false positive) - this is common with PyInstaller builds

## Troubleshooting

### "Module not found" errors
- Add missing modules to `--hidden-import` in `build_exe.py`
- Use `--collect-all=<module>` to include all submodules

### Large file size
- This is normal for PyInstaller builds (includes Python runtime and all dependencies)
- Typically 50-100MB for PyQt6 applications

### Icon not showing
- Ensure `icon.ico` is in the project root
- Try converting PNG to ICO format
- Rebuild after adding the icon

## Alternative: Using cx_Freeze

If PyInstaller doesn't work, you can use cx_Freeze:

```bash
pip install cx_Freeze
```

Create a `setup.py` file for cx_Freeze configuration.

