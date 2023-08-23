import pytest
from mkdocs import utils
from mkdocs.config.base import load_config
from mkdocs.structure.files import get_files
from mkdocs.structure.nav import get_navigation


@pytest.fixture
def make_config():
    created_configs = []

    def _make_config(mkdocs_fp=None, docs_dir=None, use_directory_urls=True, plugins={}):
        config = load_config(
            mkdocs_fp,
            docs_dir=docs_dir,
            theme={"name": "mkdocs"},
            use_directory_urls=use_directory_urls,
            plugins=plugins,
        )
        config = config.plugins.run_event("config", config)
        files = get_files(config)
        files = config.plugins.run_event("files", files, config=config)
        env = config.theme.get_env()
        nav = get_navigation(files, config)
        nav = config.plugins.run_event("nav", nav, files=files, config=config)
        #
        created_configs.append(config)
        #
        return config, files, env, nav

    yield _make_config

    for config in created_configs:
        utils.clean_directory(config.site_dir)


@pytest.fixture
def make_localized_config(make_config):
    def _make_localized_config(config, locale):
        config.plugins["i18n"].current_language = locale
        #
        config = config.plugins.run_event("config", config)
        files = get_files(config)
        files = config.plugins.run_event("files", files, config=config)
        env = config.theme.get_env()
        nav = get_navigation(files, config)
        nav = config.plugins.run_event("nav", nav, files=files, config=config)
        #
        return config, files, env, nav

    yield _make_localized_config
