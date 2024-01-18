from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import cast

from txt_utils.vocabulary_exporting import extract_vocabulary_from_text
from txt_utils_cli.default_args import add_file_arguments
from txt_utils_cli.globals import ExecutionResult
from txt_utils_cli.helper import add_mp_group, parse_path
from txt_utils_cli.logging_configuration import get_file_logger, init_and_get_console_logger


def get_vocabulary_exporting_parser(parser: ArgumentParser):
  parser.description = "This command exports the unit vocabulary."
  add_file_arguments(parser, True)
  parser.add_argument("output", type=parse_path,
                      help="output file to write the vocabulary")
  parser.add_argument("--include-empty", action="store_true",
                      help="include empty text in vocabulary if it occurs")
  add_mp_group(parser)
  return extract_vocabulary_ns


def extract_vocabulary_ns(ns: Namespace) -> ExecutionResult:
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

  voc = extract_vocabulary_from_text(
    content, ns.lsep, ns.sep, ns.include_empty, ns.n_jobs, ns.maxtasksperchild, ns.chunksize, silent=False)

  logger.info("Saving...")
  output = cast(Path, ns.output)

  voc_text = "\n".join(voc)

  try:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(voc_text, ns.encoding)
  except Exception as ex:
    logger.error("Vocabulary file couldn't be saved!")
    flogger.exception(ex)
    return False, False
  logger.info(f"Written vocabulary to: {output.absolute()}")
  del voc_text
  return True, True
