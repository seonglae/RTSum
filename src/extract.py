from typing import TypedDict
from pyopenie import OpenIE5


class Argument(TypedDict):
  text: str
  offsets: list[str]


class Extraction(TypedDict):
  arg1: Argument
  rel: Argument
  arg2s: list[Argument]
  context: None
  negated: bool
  passive: bool


class Triple(TypedDict):
  confidence: float
  sentence: str
  extraction: Extraction


def extract(text: str, host='http://localhost:8000') -> list[Triple]:
  extractor = OpenIE5(host)
  triples = extractor.extract(text)
  return triples


def triple2sentence(triple: Triple, arg2max=2) -> str:
  return triple['extraction']['arg1']['text'] + ' ' + triple['extraction']['rel']['text'] + ' ' + \
      ' '.join(
      list(map(lambda arg2: arg2['text'], triple['extraction']['arg2s']))[:arg2max]) + '.'
