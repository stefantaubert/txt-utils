from logging import getLogger

import pandas.testing
from pandas import DataFrame

from txt_utils_cli.statistics_unit_counts import get_df


def test_component():
  content = "d d\na b b\nc c c\na"
  result = get_df(content, "\n", " ", getLogger())

  assert_res = DataFrame([
    (3, "c"),
    (2, "a"),
    (2, "b"),
    (2, "d"),
  ], columns=["# Occurrences", "Unit"], index=[0, 1, 2, 3])

  pandas.testing.assert_frame_equal(result, assert_res)
