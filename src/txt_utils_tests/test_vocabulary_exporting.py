
from txt_utils.vocabulary_exporting import get_vocab


def test_get_vocab__empty_sep():
  result = get_vocab(["a b c"], "")
  assert result == {"a", "b", "c", " "}


def test_get_vocab__space_sep():
  result = get_vocab(["a b c"], " ")
  assert result == {"a", "b", "c"}
