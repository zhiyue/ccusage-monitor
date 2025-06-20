# GitHub Actions Workflows

This project uses GitHub Actions for automated testing and publishing.

## Workflows

### 1. Test Workflow (`test.yml`)
- **Trigger**: On every push and pull request
- **Purpose**: Run tests, linting, and code quality checks
- **Python versions**: 3.8, 3.9, 3.10, 3.11, 3.12
- **Actions**:
  - Install dependencies
  - Run flake8 linting
  - Run pytest with coverage
  - Upload coverage reports

### 2. Publish to Test PyPI (`publish-test.yml`)
- **Trigger**: 
  - Push to `main` branch with changes to Python files
  - Manual workflow dispatch
- **Purpose**: Test package publishing process
- **Actions**:
  - Build distribution packages
  - Check if package already exists (by hash)
  - Publish to Test PyPI if new
  - Skip if identical package exists

### 3. Publish Release to PyPI (`publish-release.yml`)
- **Trigger**:
  - Push tags starting with `v` (e.g., `v0.0.3`)
  - GitHub release published
  - Manual workflow dispatch (with dry run option)
- **Purpose**: Publish official releases to PyPI
- **Actions**:
  - Verify tag matches package version
  - Build distribution packages
  - Check if package already exists
  - Publish to PyPI if new
  - Upload build artifacts

## Usage

### Testing Changes
Every push automatically triggers tests. No action needed.

### Publishing to Test PyPI
Happens automatically when you push Python changes to `main`.

### Publishing a Release
1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Commit and push changes
4. Create and push a tag:
   ```bash
   git tag v0.0.3
   git push origin v0.0.3
   ```

### Manual Workflow Dispatch
You can manually trigger workflows from the Actions tab:
- **Test publish**: No parameters needed
- **Release publish**: Option for dry run (build without publishing)

## Secrets Required
- `PYPI_API_TOKEN`: Token for PyPI publishing
- `TEST_PYPI_API_TOKEN`: Token for Test PyPI publishing

## Benefits of Separate Workflows
1. **Clear separation**: Test vs Production publishing
2. **Different triggers**: Continuous testing vs controlled releases  
3. **Better control**: Can disable one without affecting the other
4. **Simpler logic**: Each workflow has a single responsibility
5. **Easier debugging**: Issues are isolated to specific workflows