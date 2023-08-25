# Controlling your builds

Localized versions of your site / documentation are allowed to diverge from one to another depending on your docs structure and the fallback strategy you decide to adopt with the `fallback_to_default` option.

## Diverging from the default version

The localized (non default) language structure can have files which are not present in the default language version. This allows to have localized versions of your site diverging from the default one.


===  "Non diverging"
    ```
    docs_dir
    ├── assets
    │   └── image_non_localized.png
    ├── index.fr.md
    ├── index.en.md
    ├── topic1
    │   ├── index.en.md
    │   └── index.fr.md
    ```

    will build:

    ```
    site
    ├── 404.html
    ├── assets
    │   ├── image_non_localized.png

    [...]

    ├── fr
    │   ├── index.html
    │   ├── topic1
    │   │   └── index.html
    │   └── topic2
    │       └── index.html
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

=== "Diverging"
    ```
    docs_dir
    ├── assets
    │   └── image_non_localized.png
    ├── index.fr.md
    ├── index.en.md
    ├── topic1
    │   ├── index.en.md
    │   └── index.fr.md
    └── french_only
    │   └── index.fr.md
    ```

    will build:

    ```
    site
    ├── 404.html
    ├── assets
    │   ├── image_non_localized.png

    [...]

    ├── fr
    │   ├── index.html
    │   ├── topic1
    │   │   └── index.html
    │   └── french_only     <-- only in the french /fr version
    │       └── index.html
    ├── index.html
    ├── search
    │   └── search_index.json
    ├── sitemap.xml
    ├── sitemap.xml.gz
    ├── topic1
    │   └── index.html
    ```


## Fallbacking to default

You can control whether you want the plugin to use (fallback to) the default language version of a page or resource when its localized version is missing from the docs structure.

## Option: `fallback_to_default`

|required|default|allowed values|
|---|---|---|
|no|true| true \| false|

``` yaml
plugins:
  - i18n:
    fallback_to_default: true
```

===  "fallback_to_default: true"
    ```
    docs_dir
    ├── assets
    │   └── image_non_localized.png
    ├── index.fr.md
    ├── index.en.md
    ├── topic1
    │   ├── index.en.md     <-- no french version
    ```

    will build:

    ```
    site
    ├── 404.html
    ├── assets
    │   ├── image_non_localized.png

    [...]

    ├── fr
    │   ├── index.html
    │   ├── topic1
    │   │   └── index.html      <-- built from the english version
    ├── index.html
    ├── search
    │   └── search_index.json
    ├── sitemap.xml
    ├── sitemap.xml.gz
    ├── topic1
    │   └── index.html
    ```

=== "fallback_to_default: false"
    ```
    docs_dir
    ├── assets
    │   └── image_non_localized.png
    ├── index.fr.md
    ├── index.en.md
    ├── topic1
    │   ├── index.en.md     <-- no french version
    ```

    will build:

    ```
    site
    ├── 404.html
    ├── assets
    │   ├── image_non_localized.png

    [...]

    ├── fr              <-- no topic1/ section on french version
    │   ├── index.html
    ├── index.html
    ├── search
    │   └── search_index.json
    ├── sitemap.xml
    ├── sitemap.xml.gz
    ├── topic1
    │   └── index.html
    ```
