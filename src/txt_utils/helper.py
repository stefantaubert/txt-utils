from typing import List


def split_adv(s: str, sep: str) -> List[str]:
  if sep == "":
    return list(s)
  return s.split(sep)
