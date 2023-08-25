# Interfacing with other plugins

While the `mkdocs-static-i18n` plugin does its best to be smart about its build process logic manipulation it can't possibly be aware of every other MkDocs plugin constraints.

This is a list of plugins known to work with `mkdocs-static-i18n`:

|plugin|compatible version|
|---|---|
|mkdocs-material|>=9.2.3|
|mkdocs-awesome-pages|>=2.9.1|
|mkdocs-redirects|>=1.2.1|
|mkdocs-rss-plugin|>=1.8.0|
|mkdocs-with-pdf|>=0.9.3|

If the list is not correct or that you would like another plugin to be made compatible:

- make a sample repository available with the right `requirements.txt` and `mkdocs.yml` so that we can reproduce your problem
- [open an issue](https://github.com/ultrabug/mkdocs-static-i18n/issues) and explain your use case + link the repository you've created
