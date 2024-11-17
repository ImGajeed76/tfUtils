# Installation Guide

This guide will walk you through installing TF Utils on your system. The process is straightforward and doesn't require
administrative privileges.

## Quick Installation (Recommended)

### 1. Download the Installer

1. Visit our [releases page](https://github.com/ImGajeed76/tfUtils/releases)
2. Look for the latest version
3. Download `tfutils_setup_vX.X.X.exe`
   > 💡 **Tip**: Always download the latest version to get the newest features and security updates

### 2. Run the Installer

1. Locate the downloaded `tfutils_setup_vX.X.X.exe` file
2. Double-click to run the installer
3. Follow the installation wizard:
    - Click "Next" to begin
    - Choose installation location (default is recommended)
    - **Important**: Check "Add to PATH" ✅
    - Click "Install"
    - Wait for installation to complete
    - Click "Finish"

### 3. Verify Installation

1. Close any open command prompts or terminals
2. Open a new command prompt
3. Type `tfutils` and press Enter
4. You should see the TF Utils selection menu
5. Exit by pressing `Ctrl+C` or `esc`

```bash
tfutils
```

## System Requirements

- Windows 10 or newer

## Advanced Installation Methods

### Manual Installation (For Advanced Users)

If you prefer not to use the installer, you can install TF Utils manually:

1. Download the source code
2. Install Python 3.10
3. Install Poetry
4. Run `poetry install`
5. Run `poetry run python build.py`
6. The `dist` directory will contain the built executables and installer

```bash
# Clone repository
git clone https://github.com/ImGajeed76/tfUtils.git

# Install dependencies
cd tfUtils
poetry install

# Run TF Utils
poetry run python build.py
```

## Troubleshooting

### Common Issues

#### "tfutils is not recognized"

This usually means the PATH wasn't set correctly. Solutions:

1. Run the installer again and ensure "Add to PATH" is checked
2. Or manually add the installation directory to your PATH
3. Restart your terminal/command prompt

#### "Python version conflict"

If you see Python version errors:

1. Ensure you have Python 3.10 installed
2. Uninstall other Python versions if necessary

#### Installation Fails

If the installation fails:

1. Check you have sufficient disk space
2. Download a fresh copy of the installer

### Verifying Installation Security

TF Utils provides SHA256 checksums for all releases. To verify your download:

1. Download the checksum file (`SHA256SUMS`)
2. Run in PowerShell:
   ```powershell
   Get-FileHash tfutils_setup_vX.X.X.exe -Algorithm SHA256
   ```
3. Compare the output with the checksum in `SHA256SUMS`
4. You will notice the following:
    1. "Why didn't GitHub download the file?" - Seems like it's because the file has no ending. Right-Click on the file
       and click "Open link in new tab" to download the file.
    2. "The checksum doesn't match!" - Yeah I know, currently the file doesn't provide the setup file's checksum. I will
       fix this in the future. 🙇‍♂️

## Uninstallation

To remove TF Utils:

1. **Using Windows Settings**:
    - Open Windows Settings
    - Go to Apps & Features
    - Search for "TF Utils"
    - Click Uninstall

2. **Manual Cleanup**:
    - Delete the installation directory
    - Remove the PATH entry

## Getting Help

If you encounter any installation issues:

- Search [existing issues](https://github.com/ImGajeed76/tfUtils/issues)
- Ask in our [community discussions](https://github.com/ImGajeed76/tfUtils/discussions)
- [Report a new issue](https://github.com/ImGajeed76/tfUtils/issues/new)

## Next Steps

Now that you've installed TF Utils, you might want to:

- Read the [User Guide](user-guide.md) to learn basic usage
