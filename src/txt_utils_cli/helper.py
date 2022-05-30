import argparse
import codecs
from argparse import ArgumentParser, ArgumentTypeError, _ArgumentGroup
from functools import partial
from os import cpu_count
from pathlib import Path
from shutil import copy
from typing import Callable, List, Optional
from typing import TypeVar

from ordered_set import OrderedSet

from txt_utils_cli.globals import (DEFAULT_CHUNKSIZE, DEFAULT_ENCODING, DEFAULT_MAXTASKSPERCHILD,
                                   DEFAULT_N_JOBS)

T = TypeVar("T")


# def get_split_method(sep: str) -> Callable[[str, str], List[str]]:
#   if sep == "":
#     return split_chars
#   return str.split


# def get_split_method_gen(sep: str) -> Callable[[str, str], Generator[str, None, None]]:
#   if sep == "":
#     return split_chars_gen
#   return split_gen


# def split_chars(s: str, _: str) -> List[str]:
#   return list(s)


# def split_gen(s: str, sep: str) -> Generator[str, None, None]:
#   yield from s.split(sep)


# def split_chars_gen(s: str, _: str) -> Generator[str, None, None]:
#   yield from s


def split_adv(s: str, sep: str) -> List[str]:
  if sep == "":
    return list(s)
  return s.split(sep)


def get_chunks(keys: OrderedSet[str], chunk_size: Optional[int]) -> List[OrderedSet[str]]:
  if chunk_size is None:
    chunk_size = len(keys)
  chunked_list = list(keys[i: i + chunk_size] for i in range(0, len(keys), chunk_size))
  return chunked_list


class ConvertToOrderedSetAction(argparse._StoreAction):
  def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace, values: Optional[List], option_string: Optional[str] = None):
    val = None
    if values is not None:
      val = OrderedSet(values)
    super().__call__(parser, namespace, val, option_string)


class ConvertToSetAction(argparse._StoreAction):
  def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace, values: Optional[List], option_string: Optional[str] = None):
    val = None
    if values is not None:
      val = set(values)
    super().__call__(parser, namespace, val, option_string)


def add_encoding_argument(parser: ArgumentParser, help_str: str = "encoding of the file", name: str = "--encoding") -> None:
  parser.add_argument(name, type=parse_codec, metavar='CODEC',
                      help=help_str + "; see all available codecs at https://docs.python.org/3.8/library/codecs.html#standard-encodings", default=DEFAULT_ENCODING)


def add_overwrite_argument(parser: ArgumentParser) -> None:
  parser.add_argument("-o", "--overwrite", action="store_true",
                      help="overwrite existing files")


def add_output_directory_argument(parser: ArgumentParser) -> None:
  parser.add_argument("-out", "--output-directory", metavar='PATH', type=get_optional(parse_path),
                      help="directory where to output the grids if not to the same directory")


def add_directory_argument(parser: ArgumentParser, help_str: str = "directory containing the grids") -> None:
  parser.add_argument("directory", type=parse_existing_directory, metavar="directory",
                      help=help_str)


def add_mp_group(parser: ArgumentParser) -> _ArgumentGroup:
  group = parser.add_argument_group("multiprocessing arguments")
  add_n_jobs_argument(group)
  add_chunksize_argument(group)
  add_maxtaskperchild_argument(group)
  return group


def add_n_jobs_argument(parser: ArgumentParser) -> None:
  parser.add_argument("-j", "--n-jobs", metavar='N', type=int,
                      choices=range(1, cpu_count() + 1), default=DEFAULT_N_JOBS, help="amount of parallel cpu jobs")


def parse_codec(value: str) -> str:
  pvalue = parse_required(value)
  try:
    codecs.lookup(pvalue)
  except LookupError as error:
    raise ArgumentTypeError("Codec was not found!") from error
  return pvalue


def parse_path(value: str) -> Path:
  pvalue = parse_required(value)
  try:
    path = Path(pvalue)
  except ValueError as error:
    raise ArgumentTypeError("Value needs to be a path!") from error
  return path


def parse_optional_value(value: str, method: Callable[[str], T]) -> Optional[T]:
  if value is None:
    return None
  return method(value)


def get_optional(method: Callable[[str], T]) -> Callable[[str], Optional[T]]:
  result = partial(
    parse_optional_value,
    method=method,
  )
  return result


def parse_existing_file(value: str) -> Path:
  path = parse_path(value)
  if not path.is_file():
    raise ArgumentTypeError("File was not found!")
  return path


def parse_existing_directory(value: str) -> Path:
  path = parse_path(value)
  if not path.is_dir():
    raise ArgumentTypeError("Directory was not found!")
  return path


def parse_required(value: Optional[str]) -> str:
  if value is None:
    raise ArgumentTypeError("Value must not be None!")
  return value


def parse_non_empty(value: Optional[str]) -> str:
  pvalue = parse_required(value)
  if pvalue == "":
    raise ArgumentTypeError("Value must not be empty!")
  return pvalue


def parse_non_empty_or_whitespace(value: str) -> str:
  pvalue = parse_required(value)
  if pvalue.strip() == "":
    raise ArgumentTypeError("Value must not be empty or whitespace!")
  return pvalue


def parse_float(value: str) -> float:
  pvalue = parse_required(value)
  try:
    pvalue = float(pvalue)
  except ValueError as error:
    raise ArgumentTypeError("Value needs to be a decimal number!") from error
  return pvalue


def parse_positive_float(value: str) -> float:
  pvalue = parse_float(value)
  if not pvalue > 0:
    raise ArgumentTypeError("Value needs to be greater than zero!")
  return pvalue


def parse_non_negative_float(value: str) -> float:
  pvalue = parse_float(value)
  if not pvalue >= 0:
    raise ArgumentTypeError("Value needs to be greater than or equal to zero!")
  return pvalue


def parse_integer(value: str) -> int:
  pvalue = parse_required(value)
  if not pvalue.isdigit():
    raise ArgumentTypeError("Value needs to be an integer!")
  pvalue = int(pvalue)
  return pvalue


def parse_positive_integer(value: str) -> int:
  pvalue = parse_integer(value)
  if not pvalue > 0:
    raise ArgumentTypeError("Value needs to be greater than zero!")
  return pvalue


def parse_non_negative_integer(value: str) -> int:
  pvalue = parse_integer(value)
  if not pvalue >= 0:
    raise ArgumentTypeError("Value needs to be greater than or equal to zero!")
  return pvalue


def add_chunksize_argument(parser: ArgumentParser, target: str = "lines", default: int = DEFAULT_CHUNKSIZE) -> None:
  parser.add_argument("-s", "--chunksize", type=parse_positive_integer, metavar="NUMBER",
                      help=f"amount of {target} to chunk into one job", default=default)


def add_maxtaskperchild_argument(parser: ArgumentParser) -> None:
  parser.add_argument("-m", "--maxtasksperchild", type=get_optional(parse_positive_integer), metavar="NUMBER",
                      help="amount of tasks per child", default=DEFAULT_MAXTASKSPERCHILD)


def copy_file(file_in: Path, file_out: Path) -> None:
  file_out.parent.mkdir(exist_ok=True, parents=True)
  copy(file_in, file_out)


def save_text(path: Path, text: str, encoding: str) -> None:
  #logger = getLogger(__name__)
  #logger.debug("Saving text...")
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(text, encoding=encoding)
