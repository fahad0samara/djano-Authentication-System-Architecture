# Development Guide

## Setup Development Environment

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

3. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Code Style

We follow:
- Black for code formatting
- isort for import sorting
- flake8 for linting
- Type hints for all functions

## Testing

Run tests:
```bash
pytest
```

With coverage:
```bash
pytest --cov=accounts

# Generate HTML coverage report
pytest --cov=accounts --cov-report=html
```

## Git Workflow

1. Create feature branch:
   ```bash
   git checkout -b feature/your-feature
   ```

2. Make changes and commit:
   ```bash
   git add .
   git commit -m "feat: your feature description"
   ```

3. Push and create PR:
   ```bash
   git push origin feature/your-feature
   ```