# FM26 Attribute Customizer

A GUI application for customizing attribute colours and thresholds in Football Manager 26.

## Features

- Edit attribute colour scales and thresholds
- Customize threshold values for attribute ratings
- Visual colour picker with alpha/transparency support
- Automatic backup creation before saving
- Restore from backups
- Add/remove custom ranges dynamically

## Installation

### Option 1: Download Pre-built Executable (Recommended)

1. Go to the [Releases](https://github.com/matt-wadsworth/fm-attribute-customizer/releases) page
2. Download `FM26AttributeCustomizer.exe` from the latest release
3. Run the executable (no installation required)

**Note:** Windows Defender or other antivirus software may flag the executable as suspicious. This is a false positive common with PyInstaller builds. The source code is available for review.

### Option 2: Run from Source

1. Install Python 3.8 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## Usage

1. Launch the application
2. Click "Browse" and select your FM26 installation directory
   - Steam (Windows): `C:\Program Files (x86)\Steam\steamapps\common\Football Manager 2026`
   - Gamepass `C:\XboxGames\Football Manager 2026\Content`
3. Edit attribute ranges and colours as desired
4. Click "Save Changes" to apply (backups are created automatically)
5. Use "Restore Backup" if you need to revert changes

## Bundle Files

The application edits the following Unity bundle files:
- `ui-datacollections_assets_all.bundle` - Attribute thresholds & Attribute Highlighting
- `ui-styles_assets_default.bundle` - Colour presets

**Important:** Always backup your game files before making changes. The application creates automatic backups, but it's recommended to manually backup your `bundles` folder as well.

## License
MIT