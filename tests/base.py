"""Module contains the default set of project configuration and manages the setup and build of the project.

Some parts were adapted based on the E2ETestCase class from the awesome-pages plugin
https://github.com/lukasgeiter/mkdocs-awesome-pages-plugin/blob/836098293872edda9df4576bd90759c253e1437c/mkdocs_awesome_pages_plugin/tests/e2e/base.py#L17
"""
import os
import shutil
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Generator, Optional, Tuple

import yaml
from mkdocs.config import load_config
from mkdocs.config.defaults import MkDocsConfig


class cd:
    """Context manager for changing the current working directory."""

    def __init__(self, new_path):
        self.new_path = os.path.expanduser(new_path)

    def __enter__(self):
        self.saved_path = os.getcwd()
        os.chdir(self.new_path)

    def __exit__(self, exception_type, value, traceback):
        os.chdir(self.saved_path)


def create_config(
    *, mkdocs_options: Dict[str, Any] = None, plugin_options: Dict[str, Any] = None
) -> dict:
    """Creates the default config with English and French.
    It is possible to pass 2 override dicts for the mkdocs options and plugin options respectively.
    """

    initial_mkdocs: Dict[str, Any] = {
        "site_name": "MkDocs static i18n plugin tests",
        "site_url": "http://localhost",
        "strict": True,
        "theme": {"name": "mkdocs"},
        "use_directory_urls": True,
    }

    mkdocs_result = deepcopy(initial_mkdocs)

    if mkdocs_options is not None:
        _sync_config(initial=mkdocs_result, modifications=mkdocs_options)

    # TODO Rewrite with defaultdict? lower performance, but better code lookup
    # docs_structure: both is a special value for the test, it is split into 2 different configs
    initial_plugin: Dict[str, Any] = {
        "default_language": "en",
        "default_language_only": False,
        "docs_structure": "both",
        "languages": {
            "en": {
                "build": True,
                "fixed_link": None,
                "link": "./en",
                "name": "english",
                "site_name": None,
            },
            "fr": {
                "build": True,
                "fixed_link": None,
                "link": "./fr",
                "name": "français",
                "site_name": None,
            },
        },
        "material_alternate": True,
        "nav_translations": {},
        "search_reconfigure": True,
    }

    plugin_result = deepcopy(initial_plugin)

    if plugin_options is not None:
        _sync_config(initial=plugin_result, modifications=plugin_options)

    mkdocs_result.update({"plugins": {"i18n": plugin_result}})

    return mkdocs_result


def _sync_config(*, initial: Dict[str, Any], modifications: Dict[str, Any]):
    """Replaces the initial values with the modified ones. Does not add new entries."""

    for key, value in modifications.items():
        assert key in initial
        if isinstance(value, Dict) or isinstance(initial[key], Dict):
            _sync_config(initial=initial[key], modifications=value)
        else:
            initial[key] = value


def load_configs(
    config: Dict[str, Any]
) -> Generator[Tuple[str, MkDocsConfig], None, None]:
    """Generator function that yields loaded mkdocs configs."""

    with tempfile.TemporaryDirectory(prefix="mkdocs_i18n_") as temp_directory, cd(
        temp_directory
    ):
        configs: Dict[str, Optional[MkDocsConfig]] = {
            "suffix": None,
            "folder": None,
        }

        docs_structure = config["plugins"]["i18n"]["docs_structure"]

        if docs_structure == "both":
            configs["suffix"] = _load_config(structure="suffix", config=config)
            configs["folder"] = _load_config(structure="folder", config=config)
        elif docs_structure in {"folder", "suffix"}:
            configs[docs_structure] = _load_config(
                structure=docs_structure, config=config
            )
        else:
            raise ValueError(f"docs_structure has an invalid value {docs_structure}")

        for key in list(configs.keys()):
            if configs[key] is None:
                configs.pop(key)

        for structure, mkdocs_config in configs.items():
            yield structure, mkdocs_config


def _load_config(*, structure: str, config: Dict[str, Any]) -> MkDocsConfig:
    """Loads the given config inside mkdocs."""

    plugin = config["plugins"]["i18n"]
    plugin["docs_structure"] = structure
    structure_path = Path(__file__).parent / f"docs_{structure}_structure"
    config_name = structure_path.name
    shutil.copytree(structure_path, config_name)
    Path(f"{config_name}.yml").write_text(yaml.dump(config), encoding="utf8")

    return load_config(
        config_file=f"{config_name}.yml",
        docs_dir=config_name,
        site_dir=f"site_{config_name}",
    )
