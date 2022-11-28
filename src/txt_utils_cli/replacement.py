import re
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import cast

from txt_utils_cli.default_args import add_file_and_enc_argument
from txt_utils_cli.globals import ExecutionResult
from txt_utils_cli.helper import parse_non_empty
from txt_utils_cli.logging_configuration import get_file_logger, init_and_get_console_logger


def get_replacement_parser(parser: ArgumentParser):
  parser.description = "This command replaces all matching regex patterns in the text with a custom text."
  add_file_and_enc_argument(parser)
  parser.add_argument("text", type=parse_non_empty, metavar="TEXT",
                      help="replace text")
  parser.add_argument("replace_with", type=str, metavar="REPLACE-WITH",
                      help="replace text with this text")
  parser.add_argument("-d", "--disable-regex", action="store_true",
                      help="disable parsing TEXT as regex pattern")
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

  logger.info("Replacing...")
  if ns.disable_regex:
    if ns.text not in content:
      logger.info("File did not contained TEXT. Nothing to replace.")
      return True, False
    content = content.replace(ns.text, ns.replace_with)
  else:
    pattern = re.compile(ns.text)
    content = re.sub(pattern, ns.replace_with, content)

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
