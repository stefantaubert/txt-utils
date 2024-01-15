from argparse import ArgumentParser, Namespace
from functools import partial
from multiprocessing import Pool
from pathlib import Path
from typing import List, Optional, Set, Tuple, cast

from pronunciation_dictionary import (DeserializationOptions, MultiprocessingOptions,
                                      PronunciationDict, get_weighted_pronunciation, load_dict)
from tqdm import tqdm

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


def transcribe_text_using_dict(pronunciation_dictionary: PronunciationDict, content: str, lsep: str, psep: str, wsep: str, seed: Optional[int], ignore_missing: bool, n_jobs: int, maxtasksperchild: Optional[int], chunksize: int) -> str:
  logger = init_and_get_console_logger(__name__)
  flogger = get_file_logger()

  logger.info("Splitting lines...")
  lines = content.split(lsep)
  # TODO maybe move it out and use lines as arg to be able to delete it
  del content

  flogger.debug(f"Lines: {len(lines)}")
  flogger.debug(f"Chunksize: {chunksize}")
  flogger.debug(f"Maxtask: {maxtasksperchild}")
  flogger.debug(f"Jobs: {n_jobs}")

  chunks = get_chunks(lines, chunksize)
  # chunks = chunks[:1]
  del lines

  flogger.debug(f"Chunks: {len(chunks)}")

  amount_of_jobs_required = len(chunks)
  n_jobs = min(n_jobs, amount_of_jobs_required)
  flogger.debug(f"Jobs (final): {n_jobs}")

  method_proxy = partial(
    get_vocab_process,
    wsep=wsep,
    seed=seed,
    ignore_missing=ignore_missing,
    psep=psep,
  )

  with Pool(
    processes=n_jobs,
    initializer=__init_pool,
    initargs=(chunks, pronunciation_dictionary),
    maxtasksperchild=maxtasksperchild,
  ) as pool:
    iterator = pool.imap_unordered(method_proxy, range(len(chunks)), chunksize=1)
    iterator = tqdm(iterator, total=len(chunks), desc="Processing", unit=" chunk(s)")
    result = dict(iterator)

  logger.info("Rejoining lines...")
  new_lines = (
    line if line is not None else chunks[chunk_nr][line_i]
    for chunk_nr in range(len(chunks))
    for line_i, line in enumerate(result[chunk_nr])
  )
  new_content = lsep.join(new_lines)
  del chunks
  del result
  return new_content


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
                                           ns.sep, ns.seed, ns.ignore_missing, ns.n_jobs, ns.maxtasksperchild, ns.chunksize)

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


def get_chunks(keys: List[str], chunk_size: Optional[int]) -> List[List[str]]:
  if chunk_size is None:
    chunk_size = len(keys)
  chunked_list = list(keys[i: i + chunk_size] for i in range(0, len(keys), chunk_size))
  return chunked_list


process_chunks: List[str] = None
process_dict: PronunciationDict = None


def get_vocab_process(chunk_nr: int, wsep: str, seed: Optional[int], ignore_missing: bool, psep: str) -> Tuple[int, List[str]]:
  global process_chunks
  global process_dict
  chunk = process_chunks[chunk_nr]
  return chunk_nr, get_vocab(chunk, wsep, process_dict, seed, ignore_missing, psep)


def get_vocab(lines: List[str], wsep: str, dictionary: PronunciationDict, seed: Optional[int], ignore_missing: bool, psep: str) -> Set[str]:
  new_wsep = f"{psep}{wsep}{psep}"
  new_lines = []
  for line in lines:
    words = line.split(wsep)
    words_transcribed = []
    for word in words:
      pronunciation = word
      if word not in dictionary:
        if not ignore_missing:
          continue

      pronunciations = dictionary[word]
      pronunciation = get_weighted_pronunciation(pronunciations, seed)
      pronunciation_str = psep.join(pronunciation)
      words_transcribed.append(pronunciation_str)
    new_line = new_wsep.join(words_transcribed)
    if new_line != line:
      new_lines.append(new_line)
    else:
      new_lines.append(None)

  return new_lines


def __init_pool(chunks: List[List[str]], dictionary: PronunciationDict) -> None:
  global process_chunks
  global process_dict
  process_chunks = chunks
  process_dict = dictionary
