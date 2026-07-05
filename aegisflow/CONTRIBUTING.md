# Contributing to AegisFlow

Thank you for your interest in contributing to AegisFlow!

## Development Setup

```bash
# Clone
git clone https://github.com/lanekingkong/aegisflow.git
cd aegisflow/backend

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run linter
ruff check src/
```

## Code Style

- Python: Follow PEP 8 with 4-space indentation
- JavaScript: Follow Prettier defaults
- Write meaningful commit messages (conventional commits preferred)

## Testing

All new features must include tests. We use pytest with asyncio mode.

```bash
pytest tests/ -v --cov=aegisflow --cov-report=term
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request with a clear description

## Bug Reports

Use the GitHub Issues tracker. Include:
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (Python version, OS)

## Feature Requests

Open an issue with the "enhancement" label. Describe the use case and why it matters.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
