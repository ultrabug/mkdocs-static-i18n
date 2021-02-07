# MkDocs Static I18n Plugin

*An MkDoc plugin that helps you get add multilang support to your site / documentation.*

The `mkdocs-static-i18n` plugin allows you to support multiple languages on your documentation by adding static translation files to your existing documentation pages. Multi language support is just **one .<lang>.md file away!**.

This plugin is made to be as simple as possible and will use any default page provided if there is no translation available for it!

When activated, you will get default version of your website using the `default_language` configured + one version available on `/<language>/` for every language configured in the `languages` parameter.

For example, using the following configuration on the given structure:

```
plugins:
  - i18n:
      default_language: en
      languages:
        en: 'english'
        fr: 'français'
```

```
docs_i18n
├── coconut
│   ├── index.en.md
│   └── index.fr.md
├── index.fr.md
└── index.md
```

Will build the following site (leaving out static files for readability):

```
site
├── coconut
│   └── index.html
├── en
│   ├── coconut
│   │   └── index.html
│   └── index.html
├── fr
│   ├── coconut
│   │   └── index.html
│   └── index.html
├── index.html
```

This plugin is compatible with the [MkDocs Awesome Pages Plugin](https://github.com/lukasgeiter/mkdocs-awesome-pages-plugin)!

## Configuration

All the parameters are mandatory:

- **default_language**: string
- **languages**: mapping of **language name**: **display value**

## TODO

- add docs folder + mkdocs.yml example
- add mkdocs-material example with language switcher buttons

## Contributions welcome!

Feel free to ask questions, enhancements and to contribute to this project!
