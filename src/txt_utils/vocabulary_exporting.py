from functools import partial
from logging import getLogger
from multiprocessing import Pool
from typing import List, Optional, Set, cast

from ordered_set import OrderedSet
from tqdm import tqdm

from txt_utils.helper import split_adv


def extract_vocabulary_from_text(content: str, *, line_sep: str = "\n", word_sep: str = " ", include_empty: bool = False, n_jobs: int = 4, maxtasksperchild: Optional[int] = None, chunksize: int = 10_000, silent: bool = False) -> OrderedSet[str]:
  logger = getLogger(__name__)
  logger.info("Splitting lines...")
  lines = content.split(line_sep)
  del content

  n_jobs = cast(int, n_jobs)
  chunksize = cast(int, chunksize)
  maxtasksperchild = cast(int, maxtasksperchild)

  logger.debug(f"Lines: {len(lines)}")
  logger.debug(f"Chunksize: {chunksize}")
  logger.debug(f"Maxtask: {maxtasksperchild}")
  logger.debug(f"Jobs: {n_jobs}")

  chunks = get_chunks(lines, chunksize)
  del lines

  logger.debug(f"Chunks: {len(chunks)}")

  amount_of_jobs_required = len(chunks)
  n_jobs = min(n_jobs, amount_of_jobs_required)
  logger.debug(f"Jobs (final): {n_jobs}")

  method_proxy = partial(
    get_vocab_process,
    wsep=word_sep,
  )

  voc: Set[str] = set()
  with Pool(
    processes=n_jobs,
    initializer=__init_pool,
    initargs=(chunks,),
    maxtasksperchild=maxtasksperchild,
  ) as pool:
    iterator = tqdm(pool.imap_unordered(method_proxy, range(len(chunks)), chunksize=1), total=len(chunks), desc="Processing",
                    unit=" chunk(s)", disable=silent)
    voc.update(*iterator)
  del chunks

  if not include_empty and "" in voc:
    voc.remove("")

  logger.info(f"Extracted vocabulary size: {len(voc)}")
  result = OrderedSet(sorted(voc))

  return result


def get_chunks(keys: List[str], chunk_size: Optional[int]) -> List[List[str]]:
  if chunk_size is None:
    chunk_size = len(keys)
  chunked_list = list(keys[i: i + chunk_size] for i in range(0, len(keys), chunk_size))
  return chunked_list


process_chunks: Optional[List[List[str]]] = None


def get_vocab_process(chunk_nr: int, wsep: str) -> Set[str]:
  global process_chunks
  assert process_chunks is not None
  chunk = process_chunks[chunk_nr]
  assert chunk is not None
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
