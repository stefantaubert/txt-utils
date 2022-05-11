import os
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
from txt_utils_cli.helper import parse_existing_file, parse_non_empty
from txt_utils_cli.logging_configuration import get_file_logger, init_and_get_console_logger


def get_replacement_parser(parser: ArgumentParser):
  parser.add_argument("file", type=parse_existing_file, help="text file")
  parser.add_argument("text", type=parse_non_empty,
                      help="line separator")
  parser.add_argument("replace_with", type=str, metavar="replace-with",
                      help="replace text with this text")
  return replace_ns


def replace_ns(ns: Namespace) -> ExecutionResult:
  logger = init_and_get_console_logger(__name__)
  flogger = get_file_logger()

  if ns.text == ns.replace_with:
    logger.error("Parameter 'text' and 'replace_with' need to be different!")
    return False, False

  path = cast(Path, ns.file)

  logger.info("Loading...")
  try:
    content = path.read_text(ns.encoding)
  except Exception as ex:
    logger.error("File couldn't be loaded!")
    flogger.exception(ex)
    return False, False

  if ns.text not in content:
    logger.info("File did not contained text. Nothing to replace.")
    return True, False

  logger.info("Replacing...")
  content.replace(ns.text, ns.replace_with)

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
