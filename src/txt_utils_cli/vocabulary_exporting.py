from argparse import ArgumentParser, Namespace
from functools import partial
from multiprocessing import Pool
from pathlib import Path
from typing import List, Optional, Set, cast

from tqdm import tqdm

from txt_utils_cli.default_args import add_file_arguments
from txt_utils_cli.globals import ExecutionResult
from txt_utils_cli.helper import add_mp_group, parse_path, split_adv
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
from ordered_set import OrderedSet


def extract_vocabulary_from_text(content: str, lsep: str, sep: str, include_empty: bool, n_jobs: int, maxtasksperchild: Optional[int], chunksize: int) -> OrderedSet[str]:
  logger = init_and_get_console_logger(__name__)
  flogger = get_file_logger()
  logger.info("Splitting lines...")
  lines = content.split(lsep)
  del content

  n_jobs = cast(int, n_jobs)
  chunksize = cast(int, chunksize)
  maxtasksperchild = cast(int, maxtasksperchild)

  flogger.debug(f"Lines: {len(lines)}")
  flogger.debug(f"Chunksize: {chunksize}")
  flogger.debug(f"Maxtask: {maxtasksperchild}")
  flogger.debug(f"Jobs: {n_jobs}")

  chunks = get_chunks(lines, chunksize)
  del lines

  flogger.debug(f"Chunks: {len(chunks)}")

  amount_of_jobs_required = len(chunks)
  n_jobs = min(n_jobs, amount_of_jobs_required)
  flogger.debug(f"Jobs (final): {n_jobs}")

  method_proxy = partial(
    get_vocab_process,
    wsep=sep,
  )

  voc = set()
  with Pool(
    processes=n_jobs,
    initializer=__init_pool,
    initargs=(chunks,),
    maxtasksperchild=maxtasksperchild,
  ) as pool:
    iterator = pool.imap_unordered(method_proxy, range(len(chunks)), chunksize=1)
    iterator = tqdm(iterator, total=len(chunks), desc="Processing", unit=" chunk(s)")
    voc.update(*iterator)
  del chunks

  if not include_empty and "" in voc:
    voc.remove("")

  logger.info(f"Extracted vocabulary size: {len(voc)}")
  result = OrderedSet(sorted(voc))

  return result


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

  logger.info("Splitting lines...")
  lines = content.split(ns.lsep)
  del content

  n_jobs = cast(int, ns.n_jobs)
  chunksize = cast(int, ns.chunksize)
  maxtasksperchild = cast(int, ns.maxtasksperchild)

  flogger.debug(f"Lines: {len(lines)}")
  flogger.debug(f"Chunksize: {chunksize}")
  flogger.debug(f"Maxtask: {maxtasksperchild}")
  flogger.debug(f"Jobs: {n_jobs}")

  chunks = get_chunks(lines, chunksize)
  del lines

  flogger.debug(f"Chunks: {len(chunks)}")

  amount_of_jobs_required = len(chunks)
  n_jobs = min(n_jobs, amount_of_jobs_required)
  flogger.debug(f"Jobs (final): {n_jobs}")

  method_proxy = partial(
    get_vocab_process,
    wsep=ns.sep,
  )

  voc = set()
  with Pool(
    processes=n_jobs,
    initializer=__init_pool,
    initargs=(chunks,),
    maxtasksperchild=maxtasksperchild,
  ) as pool:
    iterator = pool.imap_unordered(method_proxy, range(len(chunks)), chunksize=1)
    iterator = tqdm(iterator, total=len(chunks), desc="Processing", unit=" chunk(s)")
    voc.update(*iterator)
  del chunks

  if not ns.include_empty and "" in voc:
    voc.remove("")

  logger.info(f"Extracted vocabulary size: {len(voc)}")

  logger.info("Saving...")
  output = cast(Path, ns.output)
  voc_text = "\n".join(sorted(voc))

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


def get_chunks(keys: List[str], chunk_size: Optional[int]) -> List[List[str]]:
  if chunk_size is None:
    chunk_size = len(keys)
  chunked_list = list(keys[i: i + chunk_size] for i in range(0, len(keys), chunk_size))
  return chunked_list


process_chunks: List[str] = None


def get_vocab_process(chunk_nr: int, wsep: str) -> Set[str]:
  global process_chunks
  chunk = process_chunks[chunk_nr]
  return get_vocab(chunk, wsep)


def get_vocab(lines: List[str], wsep: str) -> Set[str]:
  voc = set()
  for line in lines:
    tokens = split_adv(line, wsep)
    voc.update(tokens)
  return voc


def __init_pool(chunks: List[List[str]]) -> None:
  global process_chunks
  process_chunks = chunks
