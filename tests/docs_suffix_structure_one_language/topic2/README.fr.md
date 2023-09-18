# Sujet 2 (french version)

!!! tip "Astuce"
    **Utilisez le sélecteur de langue dans la barre de titre** pour passer d'une version localisée à l'autre de ce site de démonstration. Ce sélecteur fait partie de [mkdocs-material >= 7.1.0](https://squidfunk.github.io/mkdocs-material/setup/changing-the-language/#site-language-selector) et est **configuré automatiquement par ce plugin** ou peut être défini de manière statique depuis le [fichier mkdocs.yml](https://github.com/ultrabug/mkdocs-static-i18n/blob/main/mkdocs.yml).

## Ce que vous voyez en ce moment

La source de cette page et son contenu média ont été localisés en suivant la
[logique de localisation](#logique-de-localisation) décrite ci-dessous. Voici
un rapide récapitulatif des fichiers utilisés comme source et de la structure
générée que vous voyez en ce moment:

```
docs
├── image.en.png
├── image.fr.png  <-- this image file is used on the /fr version
├── index.fr.md
├── index.md
├── topic1
│   ├── named_file.en.md
│   └── named_file.fr.md  <-- this file is used on the /fr version
└── topic2
    ├── index.en.md
    └── index.md
```

```
site
├── en
│   ├── image.png
│   ├── index.html
│   ├── topic1
│   │   └── named_file
│   │       └── index.html
│   └── topic2
│       └── index.html
├── fr
│   ├── image.png  <-- you see this image on the /fr version
│   ├── index.html
│   ├── topic1
│   │   └── named_file
│   │       └── index.html
│   └── topic2
│       └── index.html  <-- you are here on the /fr version
├── image.png
├── index.html
├── topic1
│   └── named_file
│       └── index.html
└── topic2
    └── index.html
```

## Localisation automatique des médias / liens / assets

![localized image](../image.png)

La source de cette image est dynamiquement localisée bien qu'elle soit
référencée dans la source du markdown par `![localized image](image.png)`.
Cela démontre que ce plugin vous permet de ne pas vous préoccuper du nom
des fichiers dans vos liens, médias et contenus statiques : utilisez leurs
noms sans extension localisée et concentrez-vous sur la traduction de vos
contenus !

---

## Logique de localisation

Ce site est construit avec cette configuration :

```
plugins:
  - i18n:
      default_language: en
      languages:
        en: english
        fr: français
```

Ce qui veut dire que nous obtiendrons trois versions de notre site :

1. la version `default_language` qui utilisera en premier les fichiers dont
l'extension est `.md` et prendra quelconque fichier en `.en.md` en repli
puisque la version `en` est configurée comme la langue par défaut
2. la version localisée `/en` qui utilisera les fichiers dont l'extension est
`.en.md` en premier et utilisera leur version `.md` en repli si elle existe
3. la version localisée `/fr` qui utilisera les fichiers dont l'extension est
`.fr.md` en premier et utilisera en repli soit la version `.en.md` (dérivée
du langage par défaut) ou `.md`

En suivant cette logique, la structure `site` générée est :

```
site
├── 404.html
├── assets
│   ├── images
│   ├── javascripts
│   └── stylesheets
├── en
│   ├── image.png
│   ├── index.html
│   ├── topic1
│   │   └── named_file
│   │       └── index.html
│   └── topic2
│       └── index.html
├── fr
│   ├── image.png
│   ├── index.html
│   ├── topic1
│   │   └── named_file
│   │       └── index.html
│   └── topic2
│       └── index.html
├── image.png
├── index.html
├── topic1
│   └── named_file
│       └── index.html
└── topic2
    └── index.html
```
