# Development Workflow

This guide explains our development process and best practices for contributing to TF Utils. Following these guidelines
helps maintain code quality and ensures a smooth collaboration experience.

## Overview

Our development workflow follows these main steps:

1. Create a feature branch
2. Develop and test your changes
3. Submit a pull request
4. Review process
5. Merge and release

## Detailed Workflow

### 1. Setting Up Your Branch

Always start your work by creating a new feature branch from the latest `main`:

```bash
# Ensure you're up to date
git fetch origin
git checkout master
git pull origin master

# Create and switch to a new branch
git checkout -b feature/my-new-feature
```

#### Branch Naming Conventions

Follow these patterns for branch names:

- `feature/` - For new features
- `fix/` - For bug fixes
- `docs/` - For documentation changes
- `refactor/` - For code restructuring
- `test/` - For adding or updating tests

Example: `feature/altium-template-support`

### 2. Development Process

#### Making Changes

1. Write your code following our style guidelines
2. Add or update tests as needed
3. Update documentation to reflect your changes
4. Ensure all pre-commit checks pass

#### Local Testing

```bash
# Run the program locally
poetry run python main.py

# Run all tests (currently pytest is not implemented)
poetry run pytest

# Run pre-commit checks (REQUIRED)
poetry run pre-commit run --all-files
```

> 💡 **Tip**: Create a `testing` folder in your root directory.
> Then instead of running `poetry run python main.py`, move to the `testing` folder and run `poetry run python ../main.py`.

#### Commit Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```bash
# Format:
# type(scope): description

# Examples:
git commit -m "feat(ui): add new project template selector"
git commit -m "fix(paths): handle network paths correctly"
git commit -m "docs: update installation instructions"
```

Common types:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code changes that neither fix bugs nor add features
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### 3. Submitting Your Work

#### Preparing for Pull Request

Before submitting:

1. Ensure all tests pass
2. Run pre-commit checks
3. Update documentation if needed
4. Write a clear PR description

```bash
# Final checks (pytest is not implemented)
poetry run pytest
poetry run pre-commit run --all-files

# Push to your fork
git push origin feature/my-new-feature
```

#### Creating the Pull Request

1. Go to the [TF Utils Repository](https://github.com/ImGajeed76/tfUtils)
2. Click "Pull requests" → "New Pull Request"
3. Select your feature branch
4. Fill in the PR template:
    - Clear description of changes
    - Related issue numbers
    - Testing performed
    - Screenshots (if UI changes)
    - Breaking changes (if any)

### 4. Review Process

#### What to Expect

1. Automated checks will run
2. Maintainers will review your code
3. You may receive change requests
4. Discussion may occur in PR comments

#### Handling Feedback

1. Review all comments
2. Make requested changes in new commits
3. Push updates to your branch
4. Respond to review comments
5. Request re-review when ready

```bash
# After making changes
git add .
git commit -m "fix: address review comments"
git push origin feature/my-new-feature
```

### 5. Merging and Cleanup

Once approved:

1. The Maintainer will merge your PR
2. You will delete your feature branch
3. And pull the latest main branch

```bash
git checkout master
git pull origin master
git branch -d feature/my-new-feature
```

## Best Practices

### Code Quality

- Write clear, self-documenting code
- Add comments for complex logic
- Keep functions focused and small
- Use meaningful variable names
- Follow type hints and docstrings

### Testing

- Write tests for new features
- Update tests for bug fixes
- Aim for good coverage
- Test edge cases
- Use meaningful test names

### Documentation

- Update docs with code changes
- Add examples for new features
- Keep README current
- Document breaking changes
- Include inline documentation
- Check for spelling and grammar

### Communication

- Be responsive to feedback
- Ask questions when unclear
- Explain complex changes
- Keep PR discussions focused
- Be respectful and professional
