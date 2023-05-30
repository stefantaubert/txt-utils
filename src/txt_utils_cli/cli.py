import argparse
import platform
import sys
from argparse import ArgumentParser
from importlib.metadata import version
from logging import getLogger
from pathlib import Path
from pkgutil import iter_modules
from tempfile import gettempdir
from time import perf_counter
from typing import Callable, Generator, List, Tuple

from txt_utils_cli.globals import ExecutionResult
from txt_utils_cli.helper import get_optional, parse_path
from txt_utils_cli.line_replacement import get_line_replacement_parser
from txt_utils_cli.logging_configuration import (configure_root_logger, get_file_logger,
                                                 try_init_file_logger)
from txt_utils_cli.merging import get_merging_parser
from txt_utils_cli.replacement import get_replacement_parser
from txt_utils_cli.statistics_unit_counts import get_unit_count_export_parser
from txt_utils_cli.transcription import get_transcription_parser
from txt_utils_cli.trimming import get_trimming_parser
from txt_utils_cli.unit_removal import get_unit_removal_parser
from txt_utils_cli.vocabulary_exporting import get_vocabulary_exporting_parser

__version__ = version("txt-utils")

INVOKE_HANDLER_VAR = "invoke_handler"

CONSOLE_PNT_GREEN = "\x1b[1;49;32m"
CONSOLE_PNT_RED = "\x1b[1;49;31m"
CONSOLE_PNT_RST = "\x1b[0m"


Parsers = Generator[Tuple[str, str, Callable[[ArgumentParser],
                                             Callable[..., ExecutionResult]]], None, None]


def formatter(prog):
  return argparse.ArgumentDefaultsHelpFormatter(prog, max_help_position=40)


def get_parsers() -> Parsers:
  yield "merge", "merge multiple text files into one", get_merging_parser
  yield "extract-vocabulary", "extract unit vocabulary", get_vocabulary_exporting_parser
  yield "transcribe", "transcribe units", get_transcription_parser
  yield "replace", "replace text", get_replacement_parser
  yield "replace-line", "replace text in a line", get_line_replacement_parser
  yield "trim-units", "trim units", get_trimming_parser
  yield "remove-units", "remove units", get_unit_removal_parser
  yield "create-unit-occurrence-stats", "create unit occurrence statistics", get_unit_count_export_parser


def print_features():
  parsers = get_parsers()
  for command, description, method in parsers:
    print(f"- `{command}`: {description}")


def _init_parser():
  main_parser = ArgumentParser(
    formatter_class=formatter,
    description="This program provides methods to modify a text file.",
  )
  main_parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
  subparsers = main_parser.add_subparsers(help="description")
  default_log_path = Path(gettempdir()) / "txt-utils.log"

  methods = get_parsers()
  for command, description, method in methods:
    method_parser = subparsers.add_parser(
      command, help=description, formatter_class=formatter)
    method_parser.set_defaults(**{
      INVOKE_HANDLER_VAR: method(method_parser),
    })
    logging_group = method_parser.add_argument_group("logging arguments")
    logging_group.add_argument("--log", type=get_optional(parse_path), metavar="FILE",
                               nargs="?", const=None, help="path to write the log", default=default_log_path)
    logging_group.add_argument("--debug", action="store_true",
                               help="include debugging information in log")

  return main_parser


def parse_args(args: List[str]) -> None:
  configure_root_logger()
  logger = getLogger()

  local_debugging = debug_file_exists()
  if local_debugging:
    logger.debug(f"Received arguments: {str(args)}")

  parser = _init_parser()

  try:
    ns = parser.parse_args(args)
  except SystemExit:
    # invalid command supplied
    return

  if hasattr(ns, INVOKE_HANDLER_VAR):
    invoke_handler: Callable[..., ExecutionResult] = getattr(ns, INVOKE_HANDLER_VAR)
    delattr(ns, INVOKE_HANDLER_VAR)
    log_to_file = ns.log is not None
    if log_to_file:
      log_to_file = try_init_file_logger(ns.log, local_debugging or ns.debug)
      if not log_to_file:
        logger.warning("Logging to file is not possible.")

    flogger = get_file_logger()
    if not local_debugging:
      sys_version = sys.version.replace('\n', '')
      flogger.debug(f"CLI version: {__version__}")
      flogger.debug(f"Python version: {sys_version}")
      flogger.debug("Modules: %s", ', '.join(sorted(p.name for p in iter_modules())))

      my_system = platform.uname()
      flogger.debug(f"System: {my_system.system}")
      flogger.debug(f"Node Name: {my_system.node}")
      flogger.debug(f"Release: {my_system.release}")
      flogger.debug(f"Version: {my_system.version}")
      flogger.debug(f"Machine: {my_system.machine}")
      flogger.debug(f"Processor: {my_system.processor}")

    flogger.debug(f"Received arguments: {str(args)}")
    flogger.debug(f"Parsed arguments: {str(ns)}")

    start = perf_counter()
    success, changed_anything = invoke_handler(ns)

    if success:
      logger.info(f"{CONSOLE_PNT_GREEN}Everything was successful!{CONSOLE_PNT_RST}")
      flogger.info("Everything was successful!")
    else:
      if log_to_file:
        logger.error(
          "Not everything was successful! See log for details.")
      else:
        logger.error(
          "Not everything was successful!")
      flogger.error("Not everything was successful!")

    if changed_anything is not None and not changed_anything:
      logger.info("Didn't change anything.")
      flogger.info("Didn't change anything.")

    duration = perf_counter() - start
    flogger.debug(f"Total duration (s): {duration}")

    if log_to_file:
      logger.info(f"Written log to: {ns.log.absolute()}")

  else:
    parser.print_help()


def run():
  arguments = sys.argv[1:]
  parse_args(arguments)


def run_prod():
  run()


def debug_file_exists():
  return (Path(gettempdir()) / "txt-utils-debug").is_file()


def create_debug_file():
  (Path(gettempdir()) / "txt-utils-debug").write_text("", "UTF-8")


if __name__ == "__main__":
  run_prod()
