import os
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Generator, List, cast

from ordered_set import OrderedSet
from tqdm import tqdm

from txt_utils_cli.globals import ExecutionResult
from txt_utils_cli.helper import (ConvertToOrderedSetAction, add_encoding_argument,
                                  parse_existing_directory, parse_existing_file,
                                  parse_non_empty_or_whitespace, parse_path)
from txt_utils_cli.logging_configuration import get_file_logger, init_and_get_console_logger


def get_merging_parser(parser: ArgumentParser):
  parser.description = "This command merges multiple files into one."
  parser.add_argument("files", type=parse_existing_file,
                      metavar="files", nargs="+", help="text files", action=ConvertToOrderedSetAction)
  parser.add_argument("output", type=parse_path, help="output text file")
  # parser.add_argument("--include", type=parse_non_empty_or_whitespace, nargs="+",
  #                     action=ConvertToOrderedSetAction, default=OrderedSet((".txt",)), help="include these file types")
  parser.add_argument("--lsep", type=str, default="\n",
                      help="separate file contents with this text while merging")
  add_encoding_argument(parser, "encoding of the text files and the output file")
  return merge_ns


def merge_ns(ns: Namespace) -> ExecutionResult:
  logger = init_and_get_console_logger(__name__)
  flogger = get_file_logger()

  # logger.info("Searching for files...")
  # file_types = set(suffix.lower() for suffix in ns.include)
  # text_files: List[Path] = list(
  #   file
  #   for folder in ns.directories
  #   for file in get_all_files_in_all_subfolders(folder)
  #   if file.suffix.lower() in file_types
  # )

  texts = []
  all_successfull = True
  for path in tqdm(ns.files, desc="Reading text files", unit=" file(s)"):
    try:
      text = path.read_text(ns.encoding)
    except Exception as ex:
      flogger(f"File: {cast(Path, path).absolute()}")
      flogger.error("File couldn't be loaded!")
      flogger.exception(ex)
      all_successfull = False
      continue
    texts.append(text)

  logger.info("Merging files...")
  text = ns.lsep.join(texts)

  logger.info("Saving merged output...")
  output = cast(Path, ns.output)

  try:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, "UTF-8")
  except Exception as ex:
    logger.error("Output couldn't be saved!")
    flogger.exception(ex)
    return False, None

  logger.info(f"Written output to: {output.absolute()}")
  return all_successfull, None


def get_all_files_in_all_subfolders(directory: Path) -> Generator[Path, None, None]:
  for root, _, files in os.walk(directory):
    for name in files:
      file_path = Path(root) / name
      yield file_path
