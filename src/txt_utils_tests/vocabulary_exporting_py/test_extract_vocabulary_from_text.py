from ordered_set import OrderedSet

from txt_utils.vocabulary_exporting import extract_vocabulary_from_text


def test_component():
  result = extract_vocabulary_from_text("b a c\nc b a", chunksize=1)
  assert result == OrderedSet(("a", "b", "c"))
