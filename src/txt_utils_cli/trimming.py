from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import cast

from tqdm import tqdm

from txt_utils_cli.default_args import add_file_arguments
from txt_utils_cli.globals import ExecutionResult
from txt_utils_cli.helper import (ConvertToSetAction, parse_non_empty)
from txt_utils_cli.logging_configuration import get_file_logger, init_and_get_console_logger


def get_trimming_parser(parser: ArgumentParser):
  parser.description = "This command trims text of units."
  add_file_arguments(parser, True)
  parser.add_argument("mode", type=str, choices=[
                      "start", "end", "both"], help="trim mode: start = only from start; end = only from end; both = start + end")
  parser.add_argument("characters", type=parse_non_empty, nargs="+",
                      help="trim these characters from each unit", action=ConvertToSetAction)
  return trim_ns


def trim_ns(ns: Namespace) -> ExecutionResult:
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

  changed_anything = False
  trim_characters = ''.join(ns.characters)
  for i, line in enumerate(tqdm(lines, desc="Trimming", unit=" line(s)")):
    units = line.split(ns.sep)
    units = (strip_str(unit, ns.mode, trim_characters) for unit in units)
    # why not?
    # symbols = (symbol for symbol in symbols if symbol != "")
    new_line = ns.sep.join(units)
    if line != new_line:
      changed_anything = True
      lines[i] = new_line

  if not changed_anything:
    return True, False

  logger.info("Rejoining lines...")
  new_content = ns.lsep.join(lines)
  del lines
  logger.info("Saving...")
  try:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(new_content, ns.encoding)
  except Exception as ex:
    logger.error("File couldn't be saved!")
    flogger.exception(ex)
    return False, False
  del content
  return True, True


def strip_str(s: str, mode: str, trim_characters: str) -> str:
  if mode == "start":
    return s.lstrip(trim_characters)

  if mode == "end":
    return s.rstrip(trim_characters)

  if mode == "both":
    return s.strip(trim_characters)

  assert False
