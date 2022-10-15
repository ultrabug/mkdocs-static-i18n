from pathlib import Path

from setuptools import find_packages, setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return (Path(__file__).resolve().parent / fname).read_text(encoding="utf-8")


setup(
    name="mkdocs-static-i18n",
    version="0.49",
    author="Ultrabug",
    author_email="ultrabug@ultrabug.net",
    description="MkDocs i18n plugin using static translation markdown files",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/ultrabug/mkdocs-static-i18n",
    download_url="https://github.com/ultrabug/mkdocs-static-i18n/tags",
    license="MIT",
    platforms="any",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["mkdocs>=1.2.3"],
    entry_points={"mkdocs.plugins": ["i18n = mkdocs_static_i18n.plugin:I18n"]},
    python_requires=">=3.7",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    project_urls={
        "Documentation": "https://github.com/ultrabug/mkdocs-static-i18n#readme",
        "Funding": "https://ultrabug.fr/#support-me",
        "Source": "https://github.com/ultrabug/mkdocs-static-i18n",
        "Tracker": "https://github.com/ultrabug/mkdocs-static-i18n/issues",
    },
)
