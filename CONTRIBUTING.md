# Contributing Guidelines

This is a demonstration project for a DevOps interview assessment. However, if you'd like to reference or learn from this code, please follow these guidelines.

## Making Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Run tests locally
5. Commit with clear messages
6. Push to your fork
7. Create a Pull Request

## Terraform Standards

- Run `terraform fmt` before committing
- Validate with `terraform validate`
- Follow the existing module structure
- Use meaningful variable names
- Keep environment configurations in `.tfvars` files

## Python Standards

- Follow PEP 8 style guide
- Include unit tests for Lambda functions
- Run tests before committing: `python test_handler.py`
- Use type hints where appropriate

## Commit Message Guidelines

Follow conventional commit format:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `chore:` - Maintenance tasks

Example: `feat: add CloudWatch alarm for Lambda errors`
