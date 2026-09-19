import shutil
import sys


def format_timestamp(seconds: float) -> str:
    """Format seconds into MM:SS.ss string."""
    minutes = int(seconds // 60)
    remainder = seconds % 60
    return f"{minutes:02d}:{remainder:05.2f}"


def require_command(command: str) -> None:
    """Verify a shell command exists in system PATH."""
    if shutil.which(command) is None:
        raise RuntimeError(
            f"'{command}' command was not found in PATH. Please install it first."
        )


def sanitize_filename(name: str) -> str:
    """Sanitize a string so it can be safely used as a filename."""
    import re
    clean = re.sub(r'[\\/*?:"<>|]', "_", name)
    clean = re.sub(r'\s+', "_", clean)
    clean = clean.strip("._ ")
    return clean or "presentation"

