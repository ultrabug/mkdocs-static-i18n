import tempfile

import pytest
from mkdocs.config.base import load_config


@pytest.fixture
def config_base():
    site_dir = tempfile.mkdtemp(prefix="mkdocs_tests_")
    return load_config("tests/mkdocs_base.yml", site_dir=site_dir)


@pytest.fixture
def config_plugin():
    site_dir = tempfile.mkdtemp(prefix="mkdocs_tests_")
    return load_config("tests/mkdocs_i18n.yml", site_dir=site_dir)
