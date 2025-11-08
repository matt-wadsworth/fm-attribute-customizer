# Release Checklist

Use this checklist when preparing a new release:

## Pre-Release

- [ ] Update version number in code (if applicable)
- [ ] Update CHANGELOG.md with new features/fixes
- [ ] Test the application thoroughly
- [ ] Build and test the executable on a clean Windows machine
- [ ] Verify all features work correctly
- [ ] Check that backups are created correctly
- [ ] Test restore functionality

## Building the Release

1. **Clean build environment:**
   ```bash
   # Remove old build artifacts
   rmdir /s /q build dist
   ```

2. **Build the executable:**
   ```bash
   python build_exe.py
   ```

3. **Test the executable:**
   - Run on a clean Windows machine (or VM)
   - Test all features
   - Verify file size is reasonable

4. **Check file size:**
   - Should be significantly smaller than 100MB after optimizations
   - Note the final size for release notes

## Creating a GitHub Release

### Option 1: Using GitHub Actions (Recommended)

1. Create and push a tag:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. GitHub Actions will automatically:
   - Build the executable
   - Create a release
   - Upload the executable and archive

### Option 2: Manual Release

1. Go to GitHub repository → Releases → Draft a new release

2. **Tag version:** `v1.0.0` (follow semantic versioning)

3. **Release title:** `FM26 Attribute Customizer v1.0.0`

4. **Description:** Copy from CHANGELOG.md for this version

5. **Attach files:**
   - `dist/FM26AttributeCustomizer.exe`
   - Optional: Create a ZIP archive with README

6. **Publish release**

## Release Notes Template

```markdown
## FM26 Attribute Customizer v1.0.0

### What's New
- Initial release
- [List key features]

### Installation
1. Download `FM26AttributeCustomizer.exe` from the assets below
2. Run the executable (no installation required)
3. Select your FM26 installation directory and start customizing!

### Requirements
- Windows 10/11
- Football Manager 2026

### Notes
- The executable may be flagged by antivirus software (false positive)
- Always backup your game files before making changes
- Automatic backups are created, but manual backups are recommended

### File Size
- Executable: ~XX MB (optimized build)
```

## Post-Release

- [ ] Update README.md if needed
- [ ] Announce the release (if applicable)
- [ ] Monitor for issues/bug reports
- [ ] Plan next version features

