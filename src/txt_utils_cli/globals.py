from os import cpu_count
from typing import Optional, Tuple

from ordered_set import OrderedSet

DEFAULT_ENCODING = "UTF-8"
DEFAULT_N_JOBS = cpu_count()
DEFAULT_CHUNKSIZE = 2000000
DEFAULT_MAXTASKSPERCHILD = None
DEFAULT_PUNCTUATION = list(OrderedSet(sorted((
  "!", "\"", "#", "$", "%", "&", "'", "(", ")", "*", "+", ",", "-", ".", "/", ":", ";", "<", "=", ">", "?", "@", "[", "\\", "]", "{", "}", "~", "`",
  "、", "。", "？", "！", "：", "；", "।", "¿", "¡", "【", "】", "，", "…", "‥", "「", "」", "『", "』", "〝", "〟", "″", "⟨", "⟩", "♪", "・", "‹", "›", "«", "»", "～", "′", "“", "”"
))))

Success = bool
ChangedAnything = bool

ExecutionResult = Tuple[Success, Optional[ChangedAnything]]
