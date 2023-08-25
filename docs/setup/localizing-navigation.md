# Localizing navigation

You can easily translate navigation items or override the whole navigation per language.

!!! tip
    The `mkdocs-static-i18n` plugin takes care of selecting the right file for you **so you never have to use their localized name**!

    Just use your page expected names (`index.md`, not `index.fr.md`) as you would on a single language site.

## Translating navigation items

This sub-option is a key/value mapping set per language as allows you to override the title of any navigation item when a matching title exists on the default language.

### Language Sub-Option: `nav_translations`

This example will translate the `Home`, `Topic1` and `Topic2` section titles to `Accueil`, `Sujet1` and `Sujet2` in the French version of the site.

``` yaml
nav:
  - Home: index.md
  - Topic1: topic1/index.md
  - Topic2: topic2/index.md

plugins:
  - i18n:
    languages:
      - locale: en
        default: true
        name: English
      - locale: fr
        name: Français
        nav_translations:
          Home: Accueil
          Topic1: Sujet1 Traduit
          Topic2: Sujet2 Traduit
```

## Overriding the navigation per language

This sub-option allows to override the whole `nav` configuration option of your `mkdocs.yml` per language. This allows to have a completely separate navigation per language!

### Language Sub-Option: `nav`

This example overrides the navigation of the French version of the site. **Mind the fact that we do not need to localize the path or file names**!

``` yaml
nav:
  - Home: index.md
  - Topic1: topic1/index.md
  - Topic2: topic2/index.md

plugins:
  - i18n:
    languages:
      - locale: en
        default: true
        name: English
      - locale: fr
        name: Français
        nav:
          - Premiere Section: topic1/index.md
          - Accueil: index.md
```
