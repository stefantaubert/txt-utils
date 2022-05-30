import re
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import cast

from tqdm import tqdm
from txt_utils_cli.default_args import add_file_arguments

from txt_utils_cli.globals import ExecutionResult
from txt_utils_cli.helper import parse_non_empty
from txt_utils_cli.logging_configuration import get_file_logger, init_and_get_console_logger


def get_line_replacement_parser(parser: ArgumentParser):
  parser.description = "This command replaces a regex pattern for each line."
  add_file_arguments(parser)
  parser.add_argument("pattern", type=parse_non_empty,
                      help="replace regex pattern")
  parser.add_argument("replace_with", type=str, metavar="replace-with",
                      help="replace pattern with this text")
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
