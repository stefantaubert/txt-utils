from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import cast

from pronunciation_dictionary import DeserializationOptions, MultiprocessingOptions, load_dict

from txt_utils.transcription import transcribe_text_using_dict
from txt_utils_cli.default_args import add_file_arguments
from txt_utils_cli.globals import ExecutionResult
from txt_utils_cli.helper import (add_encoding_argument, add_mp_group, get_optional,
                                  parse_existing_file, parse_non_negative_integer,
                                  parse_positive_integer)
from txt_utils_cli.logging_configuration import get_file_logger, init_and_get_console_logger


def get_transcription_parser(parser: ArgumentParser):
  parser.description = "This command transcribe units using a pronunciation dictionary."
  add_file_arguments(parser, True)
  parser.add_argument("dictionary", metavar="dictionary", type=parse_existing_file,
                      help="path to the pronunciation dictionary that contains pronunciations to all occurring marks")
  parser.add_argument("--psep", type=str, metavar="STRING",
                      help="pronunciations separator", default="|")
  parser.add_argument("--seed", type=get_optional(parse_non_negative_integer),
                      help="seed for choosing the pronunciation from the dictionary regarding their weights (only useful if there exist words with multiple pronunciations)", default=None)
  parser.add_argument("--ignore-missing", action="store_true",
                      help="keep marks missing in dictionary unchanged")
  mp_group = add_mp_group(parser)
  mp_group.add_argument("-sd", "--chunksize-dictionary", type=parse_positive_integer,
                        metavar="NUMBER", help="amount of lines to chunk into one job while parsing the dictionary", default=100000)
  add_deserialization_group(parser)
  return transcribe_ns


def add_deserialization_group(parser: ArgumentParser) -> None:
  group = parser.add_argument_group('deserialization arguments')
  add_encoding_argument(group, "encoding of the dictionary", "--dict-encoding")
  group.add_argument("-cc", "--consider-comments", action="store_true",
                     help="consider line comments while deserialization")
  group.add_argument("-cn", "--consider-numbers", action="store_true",
                     help="consider word numbers used to separate different pronunciations")
  group.add_argument("-cp", "--consider-pronunciation-comments", action="store_true",
                     help="consider comments in pronunciations")
  group.add_argument("-cw", "--consider-weights", action="store_true",
                     help="consider weights")


def transcribe_ns(ns: Namespace) -> ExecutionResult:
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

  mp_options = MultiprocessingOptions(ns.n_jobs, ns.maxtasksperchild, ns.chunksize_dictionary)
  options = DeserializationOptions(ns.consider_comments, ns.consider_numbers,
                                   ns.consider_pronunciation_comments, ns.consider_weights)

  logger.info("Loading dictionary...")
  try:
    pronunciation_dictionary = load_dict(ns.dictionary, ns.encoding, options, mp_options)
  except Exception as ex:
    logger = init_and_get_console_logger(__name__)
    logger.error("Pronunciation dictionary couldn't be read!")
    flogger = get_file_logger()
    flogger.exception(ex)
    return False, False

  new_content = transcribe_text_using_dict(pronunciation_dictionary, content, ns.lsep, ns.psep,
                                           ns.sep, ns.seed, ns.ignore_missing, ns.n_jobs, ns.maxtasksperchild, ns.chunksize, silent=False)

  logger.info("Saving...")

  try:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(new_content, ns.encoding)
  except Exception as ex:
    logger.error("File couldn't be saved!")
    flogger.exception(ex)
    return False, False
  del new_content
  return True, True
