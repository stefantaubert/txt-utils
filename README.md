# txt-utils

[![PyPI](https://img.shields.io/pypi/v/txt-utils.svg)](https://pypi.python.org/pypi/txt-utils)
[![PyPI](https://img.shields.io/pypi/pyversions/txt-utils.svg)](https://pypi.python.org/pypi/txt-utils)
[![MIT](https://img.shields.io/github/license/stefantaubert/txt-utils.svg)](https://github.com/stefantaubert/txt-utils/blob/main/LICENSE)

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

- add tests
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

## Dependencies

- pandas
- tqdm
- ordered-set >=4.1.0
- pronunciation-dictionary >=0.0.4

## License

MIT License

## Acknowledgments

Funded by the Deutsche Forschungsgemeinschaft (DFG, German Research Foundation) – Project-ID 416228727 – CRC 1410

## Citation

If you want to cite this repo, you can use this BibTeX-entry:

```bibtex
@misc{tstu22,
  author = {Taubert, Stefan},
  title = {txt-utils},
  year = {2022},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/stefantaubert/txt-utils}}
}
```
