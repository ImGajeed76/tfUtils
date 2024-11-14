# Contributing to TF Utils

Thanks for considering contributing to TF Utils! 🎉

## Getting Started

1. **Fork the Repository**
   - Visit: https://github.com/ImGajeed76/tfUtils
   - Click the "Fork" button

2. **Clone Your Fork**
   ```bash
   git clone https://github.com/[your-username]/tfUtils.git
   cd tfUtils
   ```

3. **Set Up Development Environment**
   ```bash
   # Install Poetry
   curl -sSL https://install.python-poetry.org | python3 -

   # Install dependencies
   poetry install

   # Set up pre-commit hooks
   poetry run pre-commit install
   ```

## Making Changes

1. **Create a Branch**
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make Your Changes**
   - Write your code
   - Add tests if needed
   - Update documentation if needed

3. **Test Your Changes**
   ```bash
   # Run tests locally
   poetry run python main.py

   # Run pre-commit checks (REQUIRED)
   poetry run pre-commit run --all-files
   ```

4. **Commit Your Changes**
   - Use clear commit messages following [Conventional Commits](https://www.conventionalcommits.org/)
   - Examples:
     ```
     feat: add new project template
     fix: correct file path handling
     docs: update installation guide
     ```

5. **Push and Create PR**
   ```bash
   git push origin feature/my-new-feature
   ```
   - Go to GitHub and create a Pull Request
   - Fill out the PR template
   - Wait for review

## Code Style Guide

- Follow PEP 8
- Use type hints where possible
- Add docstrings to functions
- Keep functions small and focused
- Use meaningful variable names

## Need Help?

- 📝 [Create an issue](https://github.com/ImGajeed76/tfUtils/issues)
- 💬 [Join discussions](https://github.com/ImGajeed76/tfUtils/discussions)
- 📧 [Contact maintainers](mailto:github.staging362@passmail.net)
