from functools import partial
from logging import getLogger
from multiprocessing import Pool
from typing import List, Optional, Tuple

from pronunciation_dictionary import PronunciationDict, get_weighted_pronunciation
from tqdm import tqdm


def transcribe_text_using_dict(content: str, pronunciation_dictionary: PronunciationDict, *, line_sep: str = "\n", word_sep: str = " ", phoneme_sep: str = "|", seed: Optional[int] = None, ignore_missing: bool = False, n_jobs: int = 4, maxtasksperchild: Optional[int] = None, chunksize: int = 10_000, silent: bool = False) -> str:
  logger = getLogger(__name__)

  logger.info("Splitting lines...")
  lines = content.split(line_sep)
  # TODO maybe move it out and use lines as arg to be able to delete it
  del content

  logger.debug(f"Lines: {len(lines)}")
  logger.debug(f"Chunksize: {chunksize}")
  logger.debug(f"Maxtask: {maxtasksperchild}")
  logger.debug(f"Jobs: {n_jobs}")

  chunks = get_chunks(lines, chunksize)
  # chunks = chunks[:1]
  del lines

  logger.debug(f"Chunks: {len(chunks)}")

  amount_of_jobs_required = len(chunks)
  n_jobs = min(n_jobs, amount_of_jobs_required)
  logger.debug(f"Jobs (final): {n_jobs}")

  method_proxy = partial(
    get_vocab_process,
    wsep=word_sep,
    seed=seed,
    ignore_missing=ignore_missing,
    psep=phoneme_sep,
  )

  with Pool(
    processes=n_jobs,
    initializer=__init_pool,
    initargs=(chunks, pronunciation_dictionary),
    maxtasksperchild=maxtasksperchild,
  ) as pool:
    iterator = tqdm(pool.imap_unordered(method_proxy, range(len(chunks)), chunksize=1), total=len(chunks), desc="Processing",
                    unit=" chunk(s)", disable=silent)
    result = dict(iterator)

  logger.info("Rejoining lines...")
  new_lines = (
    line if line is not None else chunks[chunk_nr][line_i]
    for chunk_nr in range(len(chunks))
    for line_i, line in enumerate(result[chunk_nr])
  )
  new_content = line_sep.join(new_lines)
  del chunks
  del result
  return new_content


def get_chunks(keys: List[str], chunk_size: Optional[int]) -> List[List[str]]:
  if chunk_size is None:
    chunk_size = len(keys)
  chunked_list = list(keys[i: i + chunk_size] for i in range(0, len(keys), chunk_size))
  return chunked_list


process_chunks: Optional[List[List[str]]] = None
process_dict: Optional[PronunciationDict] = None


def get_vocab_process(chunk_nr: int, wsep: str, seed: Optional[int], ignore_missing: bool, psep: str) -> Tuple[int, List[Optional[str]]]:
  global process_chunks
  global process_dict
  assert process_chunks is not None
  assert process_dict is not None
  chunk = process_chunks[chunk_nr]
  return chunk_nr, get_vocab(chunk, wsep, process_dict, seed, ignore_missing, psep)


def get_vocab(lines: List[str], wsep: str, dictionary: PronunciationDict, seed: Optional[int], ignore_missing: bool, psep: str) -> List[Optional[str]]:
  new_wsep = f"{psep}{wsep}{psep}"
  new_lines: List[Optional[str]] = []
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
