import typing
from collections import Counter
from logging import getLogger

from pandas import DataFrame
from tqdm import tqdm

from txt_utils.helper import split_adv


def get_unit_count_statistics(content: str, *, line_sep: str = "\n", word_sep: str = " ", silent: bool = False) -> DataFrame:
  logger = getLogger(__name__)
  logger.info("Splitting lines...")
  lines = content.split(line_sep)
  # del content

  total_counter: typing.Counter[str] = Counter()
  for line in tqdm(lines, desc="Calculating counts", unit=" line(s)", disable=silent):
    total_counter.update(split_adv(line, word_sep))

  logger.debug("Creating csv...")
  columns = ["# Occurrences", "Unit"]
  df = DataFrame([(v, k) for k, v in total_counter.items()], columns=columns)

  logger.debug("Sorting csv...")
  df.sort_values(["# Occurrences", "Unit"], ascending=[False, True], inplace=True, ignore_index=True)
  return df
