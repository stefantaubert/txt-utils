import re
from logging import getLogger


def replace_text(content: str, replace: str, replace_with: str, *, disable_regex: bool = False) -> str:
  logger = getLogger(__name__)

  if disable_regex and replace == replace_with:
    return content

  logger.info("Replacing...")
  if disable_regex:
    if replace not in content:
      logger.debug(f"File did not contained \"{replace}\". Nothing to replace.")
      return content
    new_content = content.replace(replace, replace_with)
  else:
    pattern = re.compile(replace)
    new_content = re.sub(pattern, replace_with, content)
  return new_content
