"""Utility functions that aren't limited to any scenario."""
from typing import Dict, Optional, TypeVar

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin

Plugin = TypeVar("Plugin", bound=BasePlugin)
"""Plugin Instance Type"""


def get_plugin(name: str, config: MkDocsConfig) -> Optional[Plugin]:
    """Returns a plugin instance"""

    plugins: Dict[str, BasePlugin] = config["plugins"]
    instance: Plugin = plugins.get(name)

    if instance:
        return instance

    scoped_name: str = f"/{name}"

    # If the plugin was not found using the name
    # then look for a theme-namespaced plugin.
    for n, p in plugins.items():
        if n.endswith(scoped_name):
            return p

    return None
