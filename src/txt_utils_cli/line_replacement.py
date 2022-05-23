import os
import re
from argparse import ArgumentParser, Namespace
from functools import partial
from math import ceil
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
from pathlib import Path
from queue import Queue
from typing import Generator, List, Optional, Set, Tuple, cast

from iterable_serialization import deserialize_iterable, serialize_iterable
from ordered_set import OrderedSet
from pronunciation_dictionary import (DeserializationOptions, MultiprocessingOptions,
                                      PronunciationDict, get_weighted_pronunciation, load_dict)
from tqdm import tqdm

from txt_utils_cli.globals import ExecutionResult
from txt_utils_cli.helper import add_encoding_argument, parse_existing_file, parse_non_empty
from txt_utils_cli.logging_configuration import get_file_logger, init_and_get_console_logger


def get_line_replacement_parser(parser: ArgumentParser):
  parser.add_argument("file", type=parse_existing_file, help="text file")
  parser.add_argument("pattern", type=parse_non_empty,
                      help="replace pattern")
  parser.add_argument("replace_with", type=str, metavar="replace-with",
                      help="replace pattern with this text")
  parser.add_argument("--lsep", type=parse_non_empty, default="\n",
                      help="line separator")
  add_encoding_argument(parser)
  return line_replace_ns


def line_replace_ns(ns: Namespace) -> ExecutionResult:
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

  pattern = re.compile(ns.pattern)
  changed_counter = 0
  for line_nr, line in enumerate(tqdm(lines, desc="Replacing", unit=" line(s)")):
    line_new = pattern.sub(ns.replace_with, line)
    if line_new != line:
      lines[line_nr] = line_new
      changed_counter += 1

  if changed_counter == 0:
    logger.info("Didn't changed anything.")
    return True, False

  logger.info(f"Changed {changed_counter} line(s).")

  logger.info("Rejoining lines...")
  content = ns.lsep.join(lines)

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
