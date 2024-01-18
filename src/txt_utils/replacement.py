import re
from logging import getLogger


def replace_text(content: str, text: str, replace_with: str, disable_regex: bool) -> str:
  logger = getLogger(__name__)

  if disable_regex and text == replace_with:
    return content

  logger.info("Replacing...")
  if disable_regex:
    if text not in content:
      logger.debug("File did not contained TEXT. Nothing to replace.")
      return content
    new_content = content.replace(text, replace_with)
  else:
    pattern = re.compile(text)
    new_content = re.sub(pattern, replace_with, content)
  return new_content
