"""
Version tracking for Artwall
This file is updated automatically on each commit via git hooks
"""

VERSION = "0.001"
COMMIT_HASH = "d4dcd51"

def get_version_string():
    """Return formatted version string"""
    return f"v{VERSION} ({COMMIT_HASH})"
