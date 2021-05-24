import tempfile

import pytest
from mkdocs.config.base import load_config


@pytest.fixture
def config_base():
    with tempfile.TemporaryDirectory(prefix="mkdocs_tests_") as site_dir:
        return load_config(
            "tests/mkdocs_base.yml", docs_dir="../docs/", site_dir=site_dir
        )


@pytest.fixture
def config_plugin():
    with tempfile.TemporaryDirectory(prefix="mkdocs_tests_") as site_dir:
        return load_config(
            "tests/mkdocs_i18n.yml", docs_dir="../docs/", site_dir=site_dir
        )


@pytest.fixture
def config_plugin_static_nav():
    with tempfile.TemporaryDirectory(prefix="mkdocs_tests_") as site_dir:
        return load_config(
            "tests/mkdocs_i18n_static_nav.yml", docs_dir="../docs/", site_dir=site_dir
        )


@pytest.fixture
def config_plugin_no_default_language():
    with tempfile.TemporaryDirectory(prefix="mkdocs_tests_") as site_dir:
        return load_config(
            "tests/mkdocs_i18n_no_default_language.yml",
            docs_dir="../docs/",
            site_dir=site_dir,
        )


@pytest.fixture
def config_plugin_translated_nav():
    with tempfile.TemporaryDirectory(prefix="mkdocs_tests_") as site_dir:
        return load_config(
            "tests/mkdocs_i18n_translated_nav.yml",
            docs_dir="../docs/",
            site_dir=site_dir,
        )
