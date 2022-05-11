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


def get_duplicates_removal_parser(parser: ArgumentParser):
  parser.add_argument("file", type=parse_existing_file, help="text file")
  parser.add_argument("--lsep", type=parse_non_empty, default="\n",
                      help="line separator")
  add_encoding_argument(parser, "encoding of the file")
  return remove_duplicates_ns


def remove_duplicates_ns(ns: Namespace) -> ExecutionResult:
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
  logger.info("Removing duplicate lines...")
  lines_new = OrderedSet(lines)

  if len(lines_new) == len(lines):
    logger.info("File contained no duplicate lines.")
    return True, False

  logger.info(f"{len(lines) - len(lines_new)} of {len(lines)} lines were duplicates.")
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
