# Utility to clean post content for modal display
# Removes title (first line), date/location (last lines), and trims blank lines

def clean_post_content(content: str) -> str:
    """
    Remove the first line (title), last 1-2 lines (date/location), and trim blank lines.
    Returns the cleaned content for modal body.
    """
        if not content:
            return '[No content available.]'
        # Replace <br> and <br/> with newlines
        content = re.sub(r'<br\s*/?>', '\n', content, flags=re.IGNORECASE)
        # Remove all other HTML tags
        content = re.sub(r'<[^>]+>', '', content)
    lines = [line.rstrip() for line in content.splitlines()]
    # Remove blank lines at start/end
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    if len(lines) == 0:
        return ''
    # Always remove the first line (title)
    lines = lines[1:]
    # If more than 2 lines remain, remove last two (date/location)
    if len(lines) > 2:
        lines = lines[:-2]
    # Remove blank lines again
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    cleaned = '\n'.join(lines)
    if not cleaned.strip():
        return '[No content available.]'
    return cleaned
