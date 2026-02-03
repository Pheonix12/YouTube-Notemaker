"""Centralized yt-dlp configuration with cookie file support."""

import os
from pathlib import Path

# Project root: two levels up from this file (src/youtube_notemake/ -> project root)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def _resolve_cookie_path(cookie_file):
    """Resolve cookie file path, trying absolute, CWD-relative, and project-root-relative."""
    path = Path(cookie_file)
    if path.is_absolute() and path.is_file():
        return str(path)
    # Try relative to CWD
    if path.is_file():
        return str(path.resolve())
    # Try relative to project root
    project_path = _PROJECT_ROOT / path
    if project_path.is_file():
        return str(project_path)
    return None


def get_base_ydl_opts(**extra_opts):
    """Build yt-dlp options with cookie file support if configured.

    Reads YT_DLP_COOKIE_FILE from environment. If set and the file exists,
    adds it to yt-dlp options to authenticate with YouTube.

    Args:
        **extra_opts: Additional yt-dlp options to include.

    Returns:
        Dict of yt-dlp options.
    """
    opts = dict(extra_opts)
    cookie_file = os.getenv("YT_DLP_COOKIE_FILE")
    if cookie_file:
        resolved = _resolve_cookie_path(cookie_file)
        if resolved:
            opts['cookiefile'] = resolved
    opts.setdefault('js_runtimes', {'node': {}})
    return opts
