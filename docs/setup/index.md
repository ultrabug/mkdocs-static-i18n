# Configuration

The `mkdocs-static-i18n` plugin offers a flexible set of options to help you localize your site as smoothly as possible.

This section contains all the details you need to succesfully get your localized site going.

!!! warning
    This documentation applies from `mkdocs-static-i18n` **version 1.0.0**.
    Users of older versions should check the [previous version 0.56 documentation](https://github.com/ultrabug/mkdocs-static-i18n/tree/0.56#readme).

## Main configuration options overview

|option|section|
|---|---|
|docs_structure|[Choosing the docs structure](choosing-the-structure.md)|
|languages|[Setting up languages](setting-up-languages.md)|
|fallback_to_default|[Controlling your builds](controlling-your-builds.md)|
|reconfigure_material|[Setting up mkdocs-material](setting-up-material.md)|
|reconfigure_search|[Setting up search](setting-up-search.md)|

## MkDocs events priority matrix

This plugin uses MkDocs event priority in order to reconfigure each of the build process steps at the less instrusive time possible to other plugins.

|build event|priority|
|---|---|
|on_config|-100|
|on_files|-100|
|on_nav|-100|
|on_env|0|
|on_template_context|50|
|on_page_markdown|50|
|on_page_context|50|
|on_post_page|-100|
|on_post_build|-100|

## Configuration example

This very documentation is built using the plugin, so it might be interesting to you [to check its mkdocs.yml](https://github.com/ultrabug/mkdocs-static-i18n/blob/main/mkdocs.yml)!
