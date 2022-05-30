
from argparse import ArgumentParser

from txt_utils_cli.helper import add_encoding_argument, parse_existing_file, parse_non_empty


def add_file_arguments(parser: ArgumentParser, include_sep: bool = False) -> None:
  add_file_and_enc_argument(parser)
  parser.add_argument("--lsep", type=parse_non_empty, metavar="STRING",
                      default="\n", help="line separator")
  if include_sep:
    add_sep_argument(parser)


def add_file_and_enc_argument(parser: ArgumentParser) -> None:
  parser.add_argument("file", type=parse_existing_file, metavar="FILE-PATH",
                      help="name of the text file")
  add_encoding_argument(parser, "encoding of the text file")


def add_sep_argument(parser: ArgumentParser) -> None:
  parser.add_argument("--sep", type=str, metavar="STRING",
                      help="unit separator", default=" ")
