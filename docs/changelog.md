# Changelog

!!!tip "Reminder"
    We try our best to follow [Semantic Versioning v2](https://semver.org/) starting from 1.0.0.

## 1.3.0 (2025-01-24)

- **build**: test and declare support for python 3.13 (#319)
- **docs**: add documentation on how to build and run the project, by Nicco Kunzmann
- **docs**: add style:check to documentation, by Nicco Kunzmann
- **docs**: fix-bad-example-for-lang-switcher-external-link-feature thx to @niccokunzmann
- **plugin**: add admonitions translations to `pymdownx.details` (#317), by Joan Puigcerver
- **plugin**: drop deprecated theme._vars and access keys directly (#315), by Joan Puigcerver
- **pyproject**: fix the doc environment used to locally serve the plugin documentation

## 1.2.3 (2024-05-02)

- **reconfigure**: drop incorrect log level from info to debug
- **reconfigure**: file.page can be None and make plugin crash

## 1.2.2 (2024-03-01)

- **build**: drop eol 3.7, add 3.12 compat and tests
- **chore**: fix deprecation warning, by Kamil Krzyśków
- **config**: new option "admonition_translations" to allow translating of admonitions by Michal Fapso (#293)
- **folder**: correct file lookup, by Kamil Krzyśków
- **plugin** fix homepage detection, by Kamil Krzyśków
- **test**: add tests for folder structure, by Kamil Krzyśków

## 1.2.1 (2024-01-28)

- **folder**: fix path lookup order, by Kamil Krzyśków
- **on_files**: switch the file localization logic to use src_uri instead of dest_uri (#279)

## 1.2.0 (2023-10-25)

- **config**: Add build_only_locale option, by Kamil Krzyśków

## 1.1.1 (2023-10-13)

- **user_overrides**: extra overrides should be applied as legacy dict, thx to @Andygol
- **docs**: add and correct lang config overrides examples

## 1.1.0 (2023-10-06)

- **material**: add a special "null" locale to generated a fixed fixed item in the lang switcher (#270)
- **reconfigure**: allow the default language to use localized files or not wrt issue #262 (#269)

## 1.0.6 (2023-09-21)

- **get_file_from_path**: resolving root path '.' should point to 'index.md', thx to @gnaegi

## 1.0.5 (2023-09-18)

- **plugin**: fix handling of files with dotted suffixes, thx to @gnaegi (#259)

## 1.0.4 (2023-09-18)

- **assets**: Handle more assets, by Kamil Krzyśków
- **plugin**: Fix build log info about directory, by Kamil Krzyśków
- **utils**: Fix logging filter class name, by Kamil Krzyśków
- **plugin**: Improve logging in general, by Kamil Krzyśków
- **plugin**: Use new filter to hide log duplicates, by Kamil Krzyśków

## 1.0.3 (2023-09-07)

- **plugin**: add support for --dirty and --dirtyreload (#249), by AngryMane
- **plugin**:  fix and improve reconfigure_search_duplicates (#253), by AngryMane
- **ci(github)**: add docs build test and deploy on push to main

## 1.0.2 (2023-08-29)

- **plugin**: on_page_context providing wrong page context data

## 1.0.1 (2023-08-29)

- **reconfigure**: base_url should handle non mandatory site_url config

## 1.0.0 (2023-08-28)

Major rewrite with breaking changes [as described and explained in this PR](https://github.com/ultrabug/mkdocs-static-i18n/pull/216).

I want to thank [Kamil Krzyśków](https://github.com/kamilkrzyskow) for his major contribution in fostering this breakthrough, his numerous direct contributions and PRs and all the time he dedicated in providing feedbacks.

A special mention to [@unverbuggt](https://github.com/unverbuggt) as well who's given the last boost of energy and feedbacks I needed to get this 1.0.0 version out!