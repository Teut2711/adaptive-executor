# Publishing to PyPI

This guide covers how to publish Adaptive Executor to PyPI for public distribution.

## Prerequisites

1. **PyPI Account**: Create account at https://pypi.org/account/register/
2. **API Token**: Generate API token at https://pypi.org/manage/account/token/
3. **Test PyPI**: Optional test account at https://test.pypi.org/

## Setup

### 1. Configure GitHub Secrets

Add your PyPI API token to GitHub repository secrets:

1. Go to: https://github.com/Teut2711/adaptive-executor/settings/secrets/actions/new
2. Name: `PYPI_API_TOKEN`
3. Value: Your PyPI API token
4. Repository access: Select repository
5. Click "Add secret"

### 2. Verify Package Configuration

Check `pyproject.toml` has:
- ✅ Package name: `adaptive-executor`
- ✅ Version: `0.1.0`
- ✅ Author and email configured
- ✅ Description and classifiers
- ✅ Optional dependencies defined

## Publishing Methods

### Method 1: Automated (Recommended)

**Tag and Push:**
```bash
# Update version in pyproject.toml
git add pyproject.toml
git commit -m "Bump version to 0.1.1"

# Create and push tag
git tag v0.1.1
git push origin v0.1.1
```

This automatically triggers the GitHub Actions workflow to:
- Build package
- Run tests
- Upload to PyPI

### Method 2: Manual

**Build and Upload:**
```bash
# Clean and build
make clean
make build

# Upload to PyPI (production)
make upload

# Or upload to Test PyPI
python -m twine upload --repository testpypi dist/*
```

## Version Management

### Semantic Versioning

Use semantic versioning: `MAJOR.MINOR.PATCH`

```bash
# Patch release (bug fixes)
git tag v0.1.1

# Minor release (new features)
git tag v0.2.0

# Major release (breaking changes)
git tag v1.0.0
```

### Version Update Checklist

Before publishing:
- [ ] Update version in `pyproject.toml`
- [ ] Update CHANGELOG.md
- [ ] Run full test suite: `make test`
- [ ] Verify build: `make build`
- [ ] Check package: `python -m twine check dist/*`
- [ ] Test installation from wheel file

## Post-Publishing

### Verification

1. **Check PyPI**: https://pypi.org/project/adaptive-executor/
2. **Test installation**:
   ```bash
   pip install adaptive-executor==0.1.1
   ```
3. **Verify imports**:
   ```python
   from adaptive_executor import AdaptiveExecutor
   ```

### Common Issues

**"File already exists"**: Version conflict - increment version
**"Invalid distribution"**: Check `pyproject.toml` syntax
**"Upload failed"**: Check PyPI token permissions

## Development Workflow

### Local Testing
```bash
# Install in development mode
make install-dev

# Run tests
make test

# Check formatting
make format

# Run linting
make lint
```

### Release Process

1. **Development**: Feature branch with changes
2. **Testing**: Full test suite passes
3. **Documentation**: Updated and built
4. **Version bump**: Update `pyproject.toml`
5. **Tag release**: `git tag v0.1.0`
6. **Publish**: Push tag triggers automated upload
7. **Verification**: Test on clean system

## Security Notes

- **Never commit** API tokens to repository
- **Use repository secrets** for sensitive data
- **Limit permissions** to minimum required
- **Rotate tokens** regularly for security

## Support

- **PyPI Documentation**: https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/
- **Twine Documentation**: https://twine.readthedocs.io/en/latest/
- **GitHub Actions**: Check Actions tab for build status
