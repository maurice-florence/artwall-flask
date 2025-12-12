import subprocess

import logging

logger = logging.getLogger(__name__)

_version_cache = None


def get_git_info():
    """
    Retrieves version info from git.
    Returns a dict with: 'version', 'commit_hash', 'last_updated'
    """
    global _version_cache
    if _version_cache:
        return _version_cache

    info = {"version": "unknown", "commit_hash": "unknown", "last_updated": "unknown"}

    try:
        # Get version from tags (e.g. v0.0.1-2-g123456)
        try:
            version = (
                subprocess.check_output(
                    ["git", "describe", "--tags", "--always", "--dirty"],
                    stderr=subprocess.DEVNULL,
                )
                .decode()
                .strip()
            )
            info["version"] = version
        except Exception:
            info["version"] = "dev"

        # Get short commit hash
        try:
            commit = (
                subprocess.check_output(
                    ["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL
                )
                .decode()
                .strip()
            )
            info["commit_hash"] = commit
        except Exception:
            pass

        # Get last commit timestamp
        try:
            # ISO 8601 format
            timestamp_str = (
                subprocess.check_output(
                    ["git", "log", "-1", "--format=%cd", "--date=iso"],
                    stderr=subprocess.DEVNULL,
                )
                .decode()
                .strip()
            )
            info["last_updated"] = timestamp_str
        except Exception:
            pass

    except Exception as e:
        logger.error(f"Error fetching git info: {e}")

    _version_cache = info
    return info
