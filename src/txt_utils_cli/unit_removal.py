from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import cast

from tqdm import tqdm

from txt_utils_cli.default_args import add_file_arguments
from txt_utils_cli.globals import ExecutionResult
from txt_utils_cli.helper import ConvertToOrderedSetAction, split_adv
from txt_utils_cli.logging_configuration import get_file_logger, init_and_get_console_logger


def get_unit_removal_parser(parser: ArgumentParser):
  parser.description = "This command removes units from lines."
  add_file_arguments(parser, True)
  parser.add_argument("units", type=str, nargs="+", metavar="UNIT-TEXT",
                      help="remove these units", action=ConvertToOrderedSetAction)
  return remove_units_ns


def remove_units_ns(ns: Namespace) -> ExecutionResult:
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

  changed_count = 0
  for i, line in enumerate(tqdm(lines, desc="Removing units", unit=" line(s)")):
    units_l = split_adv(line, ns.sep)
    units = (unit for unit in units_l if unit not in ns.units)
    new_line = ns.sep.join(units)
    if line != new_line:
      changed_count += 1
      lines[i] = new_line

  if changed_count == 0:
    return True, False

  logger.info(f"Changed {changed_count} line(s).")

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
