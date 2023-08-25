# Quick Start

!!! warning
    This documentation applies from `mkdocs-static-i18n` **version 1.0.0**.
    Users of older versions should check the [previous version 0.56 documentation](https://github.com/ultrabug/mkdocs-static-i18n/tree/0.56#readme).

After you [installed](installation.md) the plugin there are a few steps to get started.

## Choose your localization docs structure

This plugin allows you to choose how you're going to organize your localized pages.

- Using the `suffix` docs structure (default), you will suffix your files with `.<language>.<extension>` (like `index.fr.md`)
- Using the `folder` docs structure, you will create a folder per language code (like `en/` and `fr/`) and put your localized pages on those folders

Below is an example of both structures, whichever you choose is up to you, they will produce the same output.

### The suffix docs structure (default)

```
./docs_suffix_structure
├── assets
│   └── image_non_localized.png
├── image.en.png
├── image.fr.png
├── index.fr.md
├── index.en.md
├── topic1
│   ├── index.en.md
│   └── index.fr.md
└── topic2
│   ├── index.en.md
│   └── index.fr.md
```

### The folder docs structure

```
./docs_folder_structure
├── assets
│   └── image_non_localized.png
├── en
│   ├── image.png
│   ├── index.md
│   ├── topic1
│   │   └── index.md
│   └── topic2
│       └── index.md
└── fr
    ├── image.png
    ├── index.md
    ├── topic1
    │   └── index.md
    └── topic2
        └── index.md
```

## Configure the plugin in your mkdocs.yml

Once you know which structure (here we choose `suffix`) you'll use, add the plugin with its minimal configuration to support your expected languages while **choosing a default language**.

Don't worry about missing pages in the non-default language (here `fr`): they will use the default version (`en`) by default (this is configurable using the `fallback_to_default` option).

```yaml
plugins:
  - i18n:
      docs_structure: suffix
      languages:
        - locale: en
          default: true
          name: English
          build: true
        - locale: fr
          name: Français
          build: true
```

## Build and test your localized site

Congratulations, you're ready to watch your localized site live as the plugin will generate an URL path for each language:

- The default (`en`) language will reside in the root URL `/`
- The French localized (`fr`) language will reside in the `fr` URL `/fr/`

```bash
$ mkdocs serve
```

The plugin will generate the following `site` structure:

```
site
├── 404.html
├── assets
│   ├── image_non_localized.png

[...]

├── fr
│   ├── image.png
│   ├── index.html
│   ├── topic1
│   │   └── index.html
│   └── topic2
│       └── index.html
├── image.png
├── index.html
├── search
│   └── search_index.json
├── sitemap.xml
├── sitemap.xml.gz
├── topic1
│   └── index.html
└── topic2
    └── index.html
```
