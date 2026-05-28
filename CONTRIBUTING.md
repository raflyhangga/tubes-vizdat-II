# Contributing to DuniaMaskapai

This guide covers development setup, running checks locally, and understanding the CI/CD pipeline.

## Local Development Setup

### 1. Install Development Dependencies

```bash
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Install runtime dependencies
pip install -r requirements.txt

# Install development tools
pip install ruff black mypy pytest pytest-cov
```

### 2. Run Code Quality Checks Locally

**Format code with Black:**
```bash
black .
```

**Lint code with Ruff:**
```bash
ruff check . --fix
```

**Type check with mypy:**
```bash
mypy . --ignore-missing-imports --allow-untyped-defs
```

**Run all checks (recommended before committing):**
```bash
black .
ruff check . --fix
mypy . --ignore-missing-imports --allow-untyped-defs
```

## CI/CD Pipeline

GitHub Actions automatically runs the following on every push and pull request:

### 1. **Lint and Format Check** (`lint` job)
   - Runs Ruff for code style violations
   - Checks Black formatting compliance
   - **Why:** Ensures consistent code style across the project

### 2. **Type Check** (`type-check` job)
   - Runs mypy for static type validation
   - **Why:** Catches potential bugs early through type hints

### 3. **Streamlit App Verification** (`app-verify` job)
   - Verifies the main Streamlit app loads without errors
   - Creates a minimal test CSV for import testing
   - **Why:** Ensures changes don't break the core application

### 4. **Test Suite** (`tests` job)
   - Runs pytest with coverage reporting
   - Uploads coverage to Codecov
   - **Currently optional** — test suite is empty until Phase 2
   - **Why:** Automated testing as the project grows

## Branch Strategy

- **`main`** — Production-ready code
- **`chloropleth`** — Current development branch (Phase 1)
- Feature branches for Phase 2+ should be named: `feature/<description>` or `phase2/<chart-name>`

## Before Submitting a PR

1. Run all checks locally:
   ```bash
   black . && ruff check . --fix && mypy . --ignore-missing-imports --allow-untyped-defs
   ```

2. Verify the app still runs:
   ```bash
   streamlit run main.py
   ```

3. Check that all files are properly formatted:
   ```bash
   git diff --name-only | grep "\.py$"
   ```

## Adding Tests (Phase 2)

Once you're ready to add tests in Phase 2:

1. Create a `tests/` directory (if it doesn't exist)
2. Write tests using pytest:
   ```python
   # tests/test_utils.py
   import pytest
   from utils import apply_global_filters

   def test_apply_global_filters():
       # Your test here
       pass
   ```

3. Run tests locally:
   ```bash
   pytest tests/ -v --cov=./ --cov-report=html
   ```

4. The CI/CD pipeline will automatically run tests on every PR

## Configuration Files

- **`pyproject.toml`** — Black, Ruff, mypy, and pytest configuration
- **`.github/workflows/ci.yml`** — GitHub Actions workflow definition
- **`.gitignore`** — Files/folders to exclude from git

## Troubleshooting

**"No module named 'streamlit'"**
```bash
pip install -r requirements.txt
```

**Black/Ruff not formatting/checking**
```bash
# Update path and try again
black . && ruff check . --fix
```

**mypy errors on Streamlit/Plotly imports**
- This is expected — these packages don't have full type stubs
- Errors are ignored in CI via `--ignore-missing-imports`

**Tests not running**
```bash
# Verify pytest is installed
pip install pytest pytest-cov

# Run with verbose output
pytest tests/ -v
```

## Questions?

See `CLAUDE.md` for architecture and `README.md` for setup details.
