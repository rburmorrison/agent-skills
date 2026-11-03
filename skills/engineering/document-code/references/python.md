# Python Documentation

Use a concise summary followed only by applicable Google-style contract or example sections, respecting an established project format or enforced convention. Include an explanatory body only when the user explicitly requests one.

Document each caller-supplied argument under `Args:`, its meaning and relevant constraints. Do not add entries for implicit `self` or `cls`, or repeat types already clear from annotations unless tooling requires them. Use `Returns:` for a meaningful return value, or `Yields:` for a generator's yielded values. Omit an uninformative `Returns: None` section unless required by the project.

Use `Raises:` for caller-relevant exceptions, with the conditions that cause them, including propagated failures that form part of the contract. Do not list hypothetical exceptions from every underlying operation. Document public class attributes and properties where callers find their contracts; avoid duplicating the same contract across class, initializer, and property documentation.

For example, a callable used across modules can be fully documented without an explanatory body:

```python
def normalize_title(title: str) -> str:
    """Normalize a nonempty title.

    Args:
        title: Proposed title, possibly surrounded by whitespace.

    Returns:
        The title with surrounding whitespace removed.

    Raises:
        ValueError: The title is empty after whitespace is removed.
    """
    normalized = title.strip()

    if not normalized:
        raise ValueError("title must not be empty")

    return normalized
```

An obvious private formatting helper usually needs no docstring. A non-underscored helper still needs one when project linting requires it, even if no other module consumes it. Follow enforced requirements without renaming helpers, adding empty sections, or suppressing the rule to bypass them.
