from argparse import ArgumentParser, Namespace
from collections import Counter
from logging import Logger
from pathlib import Path
from typing import cast

from pandas import DataFrame
from tqdm import tqdm

from txt_utils_cli.default_args import add_file_arguments
from txt_utils_cli.globals import ExecutionResult
from txt_utils_cli.helper import parse_path, split_adv
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

  df = get_df(content, ns.lsep, ns.sep, logger)

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


def get_df(content: str, lsep: str, sep: str, logger: Logger) -> DataFrame:
  logger.info("Splitting lines...")
  lines = content.split(lsep)
  del content

  total_counter = Counter()
  lines = tqdm(lines, desc="Calculating counts", unit=" line(s)")
  for line in lines:
    total_counter.update(split_adv(line, sep))

  logger.debug("Creating csv...")
  columns = ["# Occurrences", "Unit"]
  df = DataFrame([(v, k) for k, v in total_counter.items()], columns=columns)

  logger.debug("Sorting csv...")
  df.sort_values(["# Occurrences", "Unit"], ascending=[0, 1], inplace=True, ignore_index=True)
  return df
