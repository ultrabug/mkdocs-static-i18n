import pytest
from mkdocs.commands.build import build


def navigate(nav):
    for item in nav:
        if item.children:
            for child in navigate(item.children):
                yield child
        yield item


def test_control_build(make_config):
    control_config, control_files, control_env, control_nav = make_config(
        "tests/structures/control/en_only/mkdocs.yml",
    )
    build(control_config)


@pytest.mark.parametrize(
    "control_data,test_data",
    [
        (
            {"mkdocs_fp": "tests/structures/control/en_only/mkdocs.yml"},
            {
                "mkdocs_fp": "tests/mkdocs.yml",
                "docs_dir": "docs_suffix_structure/",
                "plugins": {
                    "i18n": {
                        "languages": [
                            {"locale": "en", "name": "test", "default": True},
                        ],
                    }
                },
            },
        ),
        (
            {"mkdocs_fp": "tests/structures/control/fr_only/mkdocs.yml"},
            {
                "mkdocs_fp": "tests/mkdocs.yml",
                "docs_dir": "docs_suffix_structure/",
                "plugins": {
                    "i18n": {
                        "languages": [
                            {"locale": "fr", "name": "test", "default": True},
                        ],
                    }
                },
            },
        ),
        (
            {"mkdocs_fp": "tests/structures/control/en_only/mkdocs.yml"},
            {
                "mkdocs_fp": "tests/mkdocs.yml",
                "docs_dir": "docs_folder_structure/",
                "plugins": {
                    "i18n": {
                        "docs_structure": "folder",
                        "languages": [
                            {"locale": "en", "name": "test", "default": True},
                        ],
                    }
                },
            },
        ),
        (
            {"mkdocs_fp": "tests/structures/control/fr_only/mkdocs.yml"},
            {
                "mkdocs_fp": "tests/mkdocs.yml",
                "docs_dir": "docs_folder_structure/",
                "plugins": {
                    "i18n": {
                        "docs_structure": "folder",
                        "languages": [
                            {"locale": "fr", "name": "test", "default": True},
                        ],
                    }
                },
            },
        ),
    ],
)
def test_control_single(make_config, control_data, test_data):
    control_config, control_files, control_env, control_nav = make_config(**control_data)
    test_config, test_files, test_env, test_nav = make_config(**test_data)
    #
    assert control_nav.__str__() == test_nav.__str__()
    assert control_env.filters.keys() == test_env.filters.keys()
    assert {file.dest_uri for file in control_files} == {file.dest_uri for file in test_files}

    for control_page, test_page in zip(
        control_files.documentation_pages(), test_files.documentation_pages()
    ):
        assert control_page.dest_uri == test_page.dest_uri
        assert control_page.name == test_page.name
        assert control_page.url == test_page.url


@pytest.mark.parametrize(
    "control_data_en,control_data_fr,test_data",
    [
        (
            {"mkdocs_fp": "tests/structures/control/en_only/mkdocs.yml"},
            {"mkdocs_fp": "tests/structures/control/fr_with_default/mkdocs.yml"},
            {
                "mkdocs_fp": "tests/mkdocs.yml",
                "docs_dir": "docs_suffix_structure/",
                "plugins": {
                    "i18n": {
                        "languages": [
                            {"locale": "en", "name": "test", "default": True},
                            {"locale": "fr", "name": "test"},
                        ],
                    }
                },
            },
        ),
        (
            {"mkdocs_fp": "tests/structures/control/en_only/mkdocs.yml"},
            {"mkdocs_fp": "tests/structures/control/fr_without_default/mkdocs.yml"},
            {
                "mkdocs_fp": "tests/mkdocs.yml",
                "docs_dir": "docs_suffix_structure/",
                "plugins": {
                    "i18n": {
                        "fallback_to_default": False,
                        "languages": [
                            {"locale": "en", "name": "test", "default": True},
                            {"locale": "fr", "name": "test"},
                        ],
                    }
                },
            },
        ),
        (
            {"mkdocs_fp": "tests/structures/control/en_only/mkdocs.yml"},
            {"mkdocs_fp": "tests/structures/control/fr_with_default/mkdocs.yml"},
            {
                "mkdocs_fp": "tests/mkdocs.yml",
                "docs_dir": "docs_folder_structure/",
                "plugins": {
                    "i18n": {
                        "docs_structure": "folder",
                        "languages": [
                            {"locale": "en", "name": "test", "default": True},
                            {"locale": "fr", "name": "test"},
                        ],
                    }
                },
            },
        ),
        (
            {"mkdocs_fp": "tests/structures/control/en_only/mkdocs.yml"},
            {"mkdocs_fp": "tests/structures/control/fr_without_default/mkdocs.yml"},
            {
                "mkdocs_fp": "tests/mkdocs.yml",
                "docs_dir": "docs_folder_structure/",
                "plugins": {
                    "i18n": {
                        "fallback_to_default": False,
                        "docs_structure": "folder",
                        "languages": [
                            {"locale": "en", "name": "test", "default": True},
                            {"locale": "fr", "name": "test"},
                        ],
                    }
                },
            },
        ),
    ],
)
def test_control_en_fr(
    make_config, make_localized_config, control_data_en, control_data_fr, test_data
):
    # default

    (
        control_config_en,
        control_files_en,
        control_env_en,
        control_nav_en,
    ) = make_config(**control_data_en)
    test_config, test_files, test_env, test_nav = make_config(**test_data)

    assert control_nav_en.__str__() == test_nav.__str__()
    assert control_env_en.filters.keys() == test_env.filters.keys()
    assert {file.dest_uri for file in control_files_en} == {file.dest_uri for file in test_files}

    for control_page, test_page in zip(
        control_files_en.documentation_pages(), test_files.documentation_pages()
    ):
        assert control_page.dest_uri == test_page.dest_uri
        assert control_page.name == test_page.name
        assert control_page.url == test_page.url

    # localized

    (
        control_config_fr,
        control_files_fr,
        control_env_fr,
        control_nav_fr,
    ) = make_config(**control_data_fr)
    (
        test_config_fr,
        test_files_fr,
        test_env_fr,
        test_nav_fr,
    ) = make_localized_config(test_config, "fr")
    #
    assert control_nav_fr.__str__() == test_nav_fr.__str__()
    assert control_env_fr.filters.keys() == test_env_fr.filters.keys()

    control_dest_uris = set()
    for file in control_files_fr:
        if not file.dest_uri.startswith("assets/"):
            control_dest_uris.add(f"fr/{file.dest_uri}")
        else:
            control_dest_uris.add(file.dest_uri)
    assert control_dest_uris == {file.dest_uri for file in test_files_fr}

    control_pages = control_files_fr.documentation_pages()
    control_pages.sort(key=lambda p: p.src_uri)
    test_pages = test_files_fr.documentation_pages()
    test_pages.sort(key=lambda p: p.src_uri)

    for control_page, test_page in zip(control_pages, test_pages):
        assert f"fr/{control_page.dest_uri}" == test_page.dest_uri
        assert control_page.name == test_page.name
        if control_page.url == "./":
            assert "fr/" == test_page.url
        else:
            assert f"fr/{control_page.url}" == test_page.url
