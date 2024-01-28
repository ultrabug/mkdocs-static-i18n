"""Utility functions and classes that aren't limited to any scenario."""

import logging
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


class I18nLoggingFilter:
    """Avoid logging duplicate build time messages."""

    def __init__(self, *_, **__):
        self.filtered_prefixes = set()

    def __call__(self, record: logging.LogRecord) -> bool:
        for prefix in self.filtered_prefixes:
            if record.msg.startswith(prefix):
                return False

        return True
