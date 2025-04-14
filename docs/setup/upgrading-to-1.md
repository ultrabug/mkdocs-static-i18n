# Upgrading to 1.0.0

Already a `mkdocs-static-i18n` plugin user? Thank you! :hugging:

The plugin's configuration changed quite a lot since the previous version so I wrote [a migration script](https://github.com/ultrabug/mkdocs-static-i18n/blob/main/config_update_to_v1.py) that you just need to point to your current `mkdocs.yml` file and that will output the desired v1.0.0 YAML configuration for you!

```bash
python config_update_to_v1.py /path/to/mkdocs.yml
```
