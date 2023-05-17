from __future__ import annotations
from typing import TypedDict, Optional

from pyopenie import OpenIE5
from unicodedata import normalize
from spacy import load


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
  score: float
  parent: TripledSentence


class TripledSentence(TypedDict):
  text: str
  triples: list[Triple]
  score: float


def extract_triple(text: str, host='http://localhost:8000') -> TripledSentence:
  sentence: TripledSentence = {'text': text, 'triples': [], 'score': 0}
  extractor = OpenIE5(host)
  text = normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
  sentence['triples'] = extractor.extract(text)
  for triple in sentence['triples']:
    triple['score'] = 0
    triple['parent'] = sentence
  return sentence


def triple2sentence(triple: Triple, arg2max: Optional[int] = None) -> str:
  if arg2max is None:
    arg2max = len(triple['extraction']['arg2s'])
  return triple['extraction']['arg1']['text'] + ' ' + triple['extraction']['rel']['text'] + ' ' + \
      ' '.join(
      list(map(lambda arg2: arg2['text'], triple['extraction']['arg2s']))[:arg2max]) + '.'


def doc2sentences(docstring: str, model="en_core_web_sm") -> list[str]:
  nlp = load(model)
  document = nlp(docstring)
  return [sent.text for sent in document.sents]
