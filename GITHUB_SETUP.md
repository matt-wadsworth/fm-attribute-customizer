# GitHub Setup Guide

Follow these steps to deploy your project to GitHub and create your first release.

## Initial Setup

1. **Create a GitHub repository:**
   - Go to https://github.com/new
   - Repository name: `fm-attribute-customizer` (or your preferred name)
   - Description: "GUI application for customizing attribute colours and thresholds in Football Manager 2026"
   - Choose Public or Private
   - **Don't** initialize with README, .gitignore, or license (we already have these)

2. **Update README.md:**
   - Open `README.md`
   - Replace `YOUR_USERNAME` with your actual GitHub username in the Releases link
   - Example: `https://github.com/mw90/fm-attribute-customizer/releases`

3. **Initialize git (if not already done):**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

4. **Connect to GitHub:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/fm-attribute-customizer.git
   git branch -M main
   git push -u origin main
   ```

## Creating Your First Release

### Option 1: Automated Build with GitHub Actions

1. **Push your code:**
   ```bash
   git add .
   git commit -m "Prepare for release"
   git push
   ```

2. **Create a release tag:**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

3. **GitHub Actions will automatically:**
   - Build the executable
   - Create a release
   - Upload the files

4. **Check the Actions tab** to see the build progress

### Option 2: Manual Release

1. **Build locally:**
   ```bash
   python build_exe.py
   ```

2. **Test the executable** in `dist/FM26AttributeCustomizer.exe`

3. **Create a release on GitHub:**
   - Go to your repository → Releases → Draft a new release
   - Tag: `v1.0.0`
   - Title: `FM26 Attribute Customizer v1.0.0`
   - Description: Copy from `CHANGELOG.md`
   - Upload `dist/FM26AttributeCustomizer.exe`
   - Publish release

## GitHub Actions Setup

The workflow file (`.github/workflows/build.yml`) is already created. It will:
- Build automatically when you push a tag starting with `v`
- Create a release with the executable
- Upload both the .exe and a ZIP archive

**Note:** The workflow uses `7z` for creating archives. If you don't have 7-Zip installed on your system, you can modify the workflow to use PowerShell's `Compress-Archive` instead.

## Next Steps

1. Update `CHANGELOG.md` with your release notes
2. Consider adding screenshots to the README
3. Add a `CONTRIBUTING.md` if you want contributions
4. Set up issue templates for bug reports

## Troubleshooting

### GitHub Actions fails
- Check the Actions tab for error messages
- Ensure all dependencies are in `requirements.txt`
- Verify the build works locally first

### Executable too large
- The optimized build should be much smaller than 100MB
- Check the build warnings for excluded modules
- Consider using UPX compression (already enabled in spec file)

### Antivirus flags executable
- This is common with PyInstaller builds
- Add a note in the release about false positives
- Consider code signing (requires certificate)

