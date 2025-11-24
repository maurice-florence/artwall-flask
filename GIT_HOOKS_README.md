# Git Hooks Setup

## Auto-updating Version on Commit

The pre-commit hook automatically updates `version.py` with the current commit hash before each commit.

### Setup Instructions

The hook is already installed at `.git/hooks/pre-commit`.

On Windows, make sure you have Python in your PATH. The hook will run automatically on `git commit`.

### Manual Version Increment

To increment the version number, manually edit `version.py` and change the `VERSION` constant:

```python
VERSION = "0.002"  # Increment as needed
```

The commit hash will be automatically updated on each commit.

### How it Works

1. Before each commit, the pre-commit hook runs
2. It gets the current git commit hash using `git rev-parse --short HEAD`
3. It updates the `COMMIT_HASH` in `version.py`
4. It stages the updated file with `git add version.py`
5. The commit proceeds with the updated version file

### Version Display

The version is displayed in the top-right corner of the navbar in the format:

```text
v0.001 (abc1234)
```

Where:

- `0.001` is the manual version number
- `abc1234` is the short git commit hash
