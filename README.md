# MkDocs static i18n plugin

![mkdocs-static-i18n pypi version](https://img.shields.io/pypi/v/mkdocs-static-i18n.svg)

*An MkDocs plugin that helps you support multiple language versions of your site / documentation.*

The `mkdocs-static-i18n` plugin allows you to support multiple languages of your documentation by adding static translation files to your existing documentation pages.

Multi language support is just **one `.<language>.md` file away**!

If you want to see how it looks, [check out the demo documentation here](https://ultrabug.github.io/mkdocs-static-i18n/).

## Language detection logic

This plugin is made to be as simple as possible and will generate a default version of your website + one per configured language on the `<language>/` path.

- the `default` version will use any `.md` documentation file first and fallback to any `.<default_language>.md` file found
- the `/<language>` language versions will use any `.<language>.md` documentation file first and fallback to any `.<default_language>.md` file before fallbacking to any default `.md` file found

Since demonstrations are better than words, [check out the demo documentation here](https://ultrabug.github.io/mkdocs-static-i18n/) which showcases the logic.

## Installation

Just `pip install mkdocs-static-i18n`!

## Configuration

All the parameters are mandatory:

- **default_language**: string
- **languages**: mapping of **language name**: **display value**

```
plugins:
  - i18n:
      default_language: en
      languages:
        en: english
        fr: français
```

## Example output

Using the configuration above on the following `docs/` structure will build the following `site/` (leaving out static files for readability):

```
docs
├── index.fr.md
├── index.md
├── topic1
│   ├── index.en.md
│   └── index.fr.md
└── topic2
    ├── index.en.md
    └── index.md
```

```
site
├── en
│   ├── index.html
│   ├── topic1
│   │   └── index.html
│   └── topic2
│       └── index.html
├── fr
│   ├── index.html
│   ├── topic1
│   │   └── index.html
│   └── topic2
│       └── index.html
├── index.html
├── topic1
│   └── index.html
└── topic2
    └── index.html
```

### Not building a dedicated version for the default language

If you do not wish to build a dedicated `<language>/` path for the `default_language` version of your documentation, **simply do not list it on the `languages`** list. See issue #5 for more information.

The following configuration:

```
plugins:
  - i18n:
      default_language: en
      languages:
        fr: français
```

Applied on the following structure:

```
docs
├── index.fr.md
├── index.md
├── topic1
│   ├── index.en.md
│   └── index.fr.md
└── topic2
    ├── index.en.md
    └── index.md
```

Will build:

```
site
├── fr
│   ├── index.html
│   ├── topic1
│   │   └── index.html
│   └── topic2
│       └── index.html
├── index.html
├── topic1
│   └── index.html
└── topic2
    └── index.html
```

## Compatibility with other plugins

This plugin is compatible with the following mkdocs plugins:

- [MkDocs Material](https://github.com/squidfunk/mkdocs-material): the `search` plugin text will be switched automatically to the right language depending on the version you're browsing
- [MkDocs Awesome Pages Plugin](https://github.com/lukasgeiter/mkdocs-awesome-pages-plugin): the page ordering is preserved on the language specific versions of your site

## Adding language switcher buttons on your navigation header

Let's take `mkdocs-material` as an example and say we would like to add two buttons to allow our visitors to switch to their preferred language.

The following explanation is showcased in the demo website and you can find the files in this very repository:

- [mkdocs.yml](https://github.com/ultrabug/mkdocs-static-i18n/tree/main/mkdocs.yml)
- [theme_overrides](https://github.com/ultrabug/mkdocs-static-i18n/tree/main/theme_overrides)

We need to add a `custom_dir` to our `theme` configuration:

```
theme:
  name: material
  custom_dir: theme_overrides
```

Then override the `header.html` to insert something like:

```
    {% if "i18n" in config.plugins %}
      <div style="margin-left: 10px; margin-right: 10px;">
          {% include "partials/i18n_languages.html" %}
      </div>
    {% endif %}
```

And add a `i18n_languages.html` that could look like this:

```
{% for lang, display in config.plugins.i18n.config.languages.items() -%}
    <div style="display: inline-block; margin-right:5px;"><a href="/{{ lang }}/">{{ display }}</a></div>
{% endfor %}
```

The resulting files should be placed like this:

```
theme_overrides
└── partials
    ├── header.html
    └── i18n_languages.html
```

## See it in action!

- [On this repository demo website](https://ultrabug.github.io/mkdocs-static-i18n/)
- [On my own website: ultrabug.fr](https://ultrabug.fr)

## Contributions welcome!

Feel free to ask questions, enhancements and to contribute to this project!
