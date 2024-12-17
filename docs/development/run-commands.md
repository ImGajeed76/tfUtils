# Running Commands in Different Operating Systems

## Windows (PowerShell)

1. Opening PowerShell:
    - Press `Win + X` and select "Windows PowerShell" or "Terminal"
    - OR press `Win + R`, type `powershell`, and press Enter
    - OR search for "PowerShell" in the Start menu

2. Navigating directories (if needed):
   ```powershell
   # List current directory contents
   dir
   # OR
   ls

   # Change directory (e.g., C:\Users\<YourUsername>\Desktop)
   cd path\to\your\folder

   # Go up one directory
   cd ..

   # Go to your home directory (usually C:\Users\<YourUsername>)
   cd ~
   ```

3. Running commands:
   ```powershell
   # Example commands
   python --version
   npm --version
   java --version
   ```

   Just paste the command and press Enter. Make sure you know what the command does before running it!

## Mac (Terminal)

1. Opening Terminal:
    - Press `Command + Space` to open Spotlight
    - Type "Terminal" and press Enter
    - OR find Terminal in Applications → Utilities → Terminal

2. Navigating directories (if needed):
   ```bash
   # List current directory contents
   ls

   # Change directory
   cd path/to/your/folder

   # Go up one directory
   cd ..

   # Go to your home directory
   cd ~
   ```

3. Running commands:
   ```bash
   # Example commands
   python3 --version
   npm --version
   java --version
   ```

   Just paste the command and press Enter. Make sure you know what the command does before running it!

## Linux (Terminal)

1. Opening Terminal:
    - Press `Ctrl + Alt + T` (on most distributions)
    - OR search for "Terminal" in your application menu

2. Navigating directories (if needed):
   ```bash
   # List current directory contents
   ls

   # Change directory
   cd path/to/your/folder

   # Go up one directory
   cd ..

   # Go to your home directory
   cd ~
   ```

3. Running commands:
   ```bash
   # Example commands
   python3 --version
   npm --version
   java --version
   ```

   Just paste the command and press Enter. Make sure you know what the command does before running it!

## Common Tips

- Use `Tab` for auto-completion of file and folder names
- Use `↑` and `↓` arrow keys to navigate through command history
- Use `Ctrl + C` (Command + C on Mac) to cancel a running command
- Use `clear` to clear the terminal screen
- Use `pwd` to show your current directory path

## Troubleshooting

If a command is not found:

1. Verify the program is installed
2. Check if the program is in your system's PATH
3. Try using the full path to the program
4. On Windows, you might need to restart PowerShell after installing new programs

For example, if `python --version` doesn't work:

- Windows: Try `py --version` or check if Python is in your PATH
- Mac/Linux: Try `python3 --version` as many systems use this command instead

Remember: Commands are case-sensitive on Mac and Linux, but not on Windows.
