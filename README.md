# txt-utils

[![PyPI](https://img.shields.io/pypi/v/txt-utils.svg)](https://pypi.python.org/pypi/txt-utils)
[![PyPI](https://img.shields.io/pypi/pyversions/txt-utils.svg)](https://pypi.python.org/pypi/txt-utils)
[![MIT](https://img.shields.io/github/license/stefantaubert/txt-utils.svg)](https://github.com/stefantaubert/txt-utils/blob/master/LICENSE)
[![PyPI](https://img.shields.io/pypi/wheel/txt-utils.svg)](https://pypi.python.org/pypi/txt-utils)
[![PyPI](https://img.shields.io/pypi/implementation/txt-utils.svg)](https://pypi.python.org/pypi/txt-utils)
[![PyPI](https://img.shields.io/github/commits-since/stefantaubert/txt-utils/latest/master.svg)](https://github.com/stefantaubert/txt-utils/compare/v0.0.3...master)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10571273.svg)](https://doi.org/10.5281/zenodo.10571273)

CLI to modify text files.

## Features

- `merge`: merge multiple text files into one
- `extract-vocabulary`: extract unit vocabulary
- `transcribe`: transcribe units
- `replace`: replace text
- `replace-line`: replace text in a line
- `trim-units`: trim units
- `remove-units`: remove units
- `create-unit-occurrence-stats`: create unit occurrence statistics

## Roadmap

- create n-grams
- map units
- merge units right/left
- calculate units TF-IDF

## Installation

```sh
pip install txt-utils --user
```

## Usage

```sh
txt-utils-cli
```

## Development setup

```sh
# update
sudo apt update
# install Python 3.8-3.12 for ensuring that tests can be run
sudo apt install python3-pip \
  python3.8 python3.8-dev python3.8-distutils python3.8-venv \
  python3.9 python3.9-dev python3.9-distutils python3.9-venv \
  python3.10 python3.10-dev python3.10-distutils python3.10-venv \
  python3.11 python3.11-dev python3.11-distutils python3.11-venv \
  python3.12 python3.12-dev python3.12-distutils python3.12-venv
# install pipenv for creation of virtual environments
python3.8 -m pip install pipenv --user

# check out repo
git clone https://github.com/stefantaubert/txt-utils.git
cd txt-utils
# create virtual environment
python3.8 -m pipenv install --dev
```

## Running the tests

```sh
# first install the tool like in "Development setup"
# then, navigate into the directory of the repo (if not already done)
cd txt-utils
# activate environment
python3.8 -m pipenv shell
# run tests
tox
```

Final lines of test result output:

```log
  py38: commands succeeded
  py39: commands succeeded
  py310: commands succeeded
  py311: commands succeeded
  py312: commands succeeded
  congratulations :)
```

## License

MIT License

## Acknowledgments

Funded by the Deutsche Forschungsgemeinschaft (DFG, German Research Foundation) – Project-ID 416228727 – CRC 1410

## Citation

If you want to cite this repo, you can use the BibTeX-entry generated by GitHub (see *About => Cite this repository*).

```txt
Taubert, S. (2024). txt-utils (Version 0.0.3) [Computer software]. https://doi.org/10.5281/zenodo.10571273
```
