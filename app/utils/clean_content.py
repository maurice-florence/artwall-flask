# Utility to clean post content for modal display
# Removes title (first line), date/location (last lines), and trims blank lines

def clean_post_content(content: str) -> str:
    """
    Remove the first line (title), last 1-2 lines (date/location), and trim blank lines.
    Returns the cleaned content for modal body.
    """
    if not content:
        return ''
    lines = [line.rstrip() for line in content.splitlines()]
    # Remove blank lines at start/end
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    if len(lines) <= 3:
        # Not enough lines to clean, just return joined
        return '\n'.join(lines)
    # Remove first line (title)
    lines = lines[1:]
    # Remove last two lines (date/location)
    lines = lines[:-2]
    # Remove blank lines again
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return '\n'.join(lines)
