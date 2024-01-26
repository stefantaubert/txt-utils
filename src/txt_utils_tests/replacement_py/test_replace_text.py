from txt_utils.replacement import replace_text


def test_component_regex():
  result = replace_text("abc test", r"[abc]", r"x")
  assert result == "xxx test"


def test_component_no_regex():
  result = replace_text("abc test", r"[abc]", r"x", disable_regex=True)
  assert result == "abc test"
