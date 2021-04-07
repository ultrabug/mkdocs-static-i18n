# Home page (default version + english version)

This is the home page displayed from the `index.md` file.

The settings used to build this site is:

```
plugins:
  - i18n:
      default_language: en
      languages:
        en: english
        fr: français
```

Meaning that we will get three versions of our website:

1. the `default_language` version which will use any `.md` documentation file first and fallback to any `.en.md` file found since `en` is the default language
2. the `/en` language version which will use any `.en.md` documentation file first and fallback to any `.md` file found
3. the `/fr` language version which will use any `.fr.md` documentation file first and fallback to either `.en.md` file (default language) or `.md` file (default language fallback) whichever comes first

Given that logic, the following page is displayed on both the default language version and the /en version.

```
docs
├── index.fr.md
├── index.md  <-- you are here
├── topic1
│   ├── named_file.en.md
│   └── named_file.fr.md
└── topic2
    ├── index.en.md
    └── index.md
```

Use the **language switcher in the header** to switch between the localized
versions of the website. This switcher is part of [mkdocs-material >= 7.1.0](https://squidfunk.github.io/mkdocs-material/setup/changing-the-language/#site-language-selector) and is configured from the [mkdocs.yml file](https://github.com/ultrabug/mkdocs-static-i18n/blob/main/mkdocs.yml).
