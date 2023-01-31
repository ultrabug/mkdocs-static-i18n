def value_in_frontmatter(key, metadata):
    """Check if a key exists in the frontmatter.

    Args:
        key (any): the key to check
        metadata (any): the frontmatter

    Returns:
        bool: true if exists
    """
    if key in metadata:
        return metadata[key]
    else:
        return None


def on_env(env, config, files, **kwargs):
    env.filters["value_in_frontmatter"] = value_in_frontmatter
    return env
