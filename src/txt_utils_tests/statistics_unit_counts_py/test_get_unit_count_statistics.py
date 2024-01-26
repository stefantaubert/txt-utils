import pandas.testing
from pandas import DataFrame

from txt_utils.statistics_unit_counts import get_unit_count_statistics


def test_component():
  content = "d d\na b b\nc c c\na d"
  result = get_unit_count_statistics(content)

  assert_res = DataFrame([
    (3, "c"),
    (3, "d"),
    (2, "a"),
    (2, "b"),
  ], columns=["# Occurrences", "Unit"], index=[0, 1, 2, 3])

  pandas.testing.assert_frame_equal(result, assert_res)
