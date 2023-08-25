# Choosing the docs structure

Depending on your project size and personal taste, you are free to choose a `docs/` structure that will allow you to organize your localized pages and resources using the `docs_structure` configuration option.

## Option: `docs_structure`

|required|default|allowed values|
|---|---|---|
|yes|suffix| suffix \| folder|

``` yaml
plugins:
  - i18n:
    docs_structure: suffix
```

## The suffix structure

Using the `suffix` docs structure (default), you will suffix your files with `.<language>.<extension>` (like `index.fr.md`).

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

## The folder structure

Using the `folder` docs structure, you will create a folder per language code (like `en/` and `fr/`) and put your localized pages on those folders.

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