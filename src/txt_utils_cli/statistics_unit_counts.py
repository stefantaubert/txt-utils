from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import cast

from txt_utils.statistics_unit_counts import get_unit_count_statistics
from txt_utils_cli.default_args import add_file_arguments
from txt_utils_cli.globals import ExecutionResult
from txt_utils_cli.helper import parse_path
from txt_utils_cli.logging_configuration import get_file_logger, init_and_get_console_logger


def get_unit_count_export_parser(parser: ArgumentParser):
  parser.description = "This command creates a CSV containing statistical information about the unit occurrences."
  add_file_arguments(parser, True)
  parser.add_argument("output", type=parse_path, help="output .csv")
  return get_word_count_ns


def get_word_count_ns(ns: Namespace) -> ExecutionResult:
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

  df = get_unit_count_statistics(content, line_sep=ns.lsep, word_sep=ns.sep, silent=False)

  logger.info("Saving...")

  try:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ns.output, sep=";", header=True, index=False, encoding=ns.encoding)
  except Exception as ex:
    logger.error("Output couldn't be saved!")
    flogger.exception(ex)
    return False, False
  logger.info(f"Saved output to: \"{ns.output.absolute()}\".")
  return True, True
