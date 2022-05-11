import os
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Generator, List, cast

from ordered_set import OrderedSet
from tqdm import tqdm

from txt_utils_cli.globals import ExecutionResult
from txt_utils_cli.helper import (ConvertToOrderedSetAction, add_encoding_argument,
                                  parse_existing_directory, parse_existing_file, parse_non_empty,
                                  parse_non_empty_or_whitespace, parse_path)
from txt_utils_cli.logging_configuration import get_file_logger, init_and_get_console_logger


def get_sorting_parser(parser: ArgumentParser):
  parser.add_argument("file", type=parse_existing_file, help="text file")
  parser.add_argument("--lsep", type=parse_non_empty, default="\n",
                      help="line separator")
  parser.add_argument("--desc", action="store_true", help="sort descending; default is ascending")
  add_encoding_argument(parser, "encoding of the file")
  return sort_ns


def sort_ns(ns: Namespace) -> ExecutionResult:
  logger = init_and_get_console_logger(__name__)
  flogger = get_file_logger()
  path = cast(Path, ns.file)
  logger.info("Loading...")
  try:
    content = path.read_text(ns.encoding)
  except Exception as ex:
    logger.error("File couldn't be loaded!")
    flogger.exception(ex)
    return False, False

  logger.info("Splitting lines...")
  lines = content.split(ns.lsep)
  del content

  logger.info("Sorting lines...")
  lines_new = sorted(lines, reverse=ns.desc)

  if lines_new == lines:
    logger.info("File was already sorted.")
    return True, False
  del lines

  logger.info("Rejoining lines...")
  content = ns.lsep.join(lines_new)
  del lines_new

  logger.info("Saving...")
  try:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, ns.encoding)
  except Exception as ex:
    logger.error("File couldn't be saved!")
    flogger.exception(ex)
    return False, False
  del content
  return True, True
