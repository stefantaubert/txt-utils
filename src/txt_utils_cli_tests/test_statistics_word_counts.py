from logging import getLogger

import pandas.testing
from pandas import DataFrame

from txt_utils_cli.statistics_word_counts import get_df


def test_component():
  content = "d d\na b b\nc c c\na"
  result = get_df(content, "\n", " ", getLogger())

  assert_res = DataFrame([
    ("c", 3),
    ("a", 2),
    ("b", 2),
    ("d", 2),
  ], columns=["Unit", "# Occurrences"], index=[0, 1, 2, 3])

  pandas.testing.assert_frame_equal(result, assert_res)
