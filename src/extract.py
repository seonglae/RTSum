from __future__ import annotations
from time import time
from typing import TypedDict, Optional
from os import getenv
from unicodedata import normalize
from re import sub

from dotenv import load_dotenv
from pyopenie import OpenIE5
from spacy import load

load_dotenv()


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


def extract_triple(text: str, host=None) -> TripledSentence:
  if host is None:
    host = getenv('OPENIE_URL')
  sentence: TripledSentence = {'text': text, 'triples': [], 'score': 0}
  extractor = OpenIE5(host)
  text = normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
  sentence['triples'] = extractor.extract(text)
  for triple in sentence['triples']:
    triple['score'] = 0
    triple['parent'] = sentence
    extraction = triple['extraction']
    extraction['arg1']['text'] = sub(r"\((.*?)\)|\(|\)|\[|\]", r'', extraction['arg1']['text'])
    extraction['rel']['text'] = sub(r"\((.*?)\)|\(|\)|\[|\]", r'', extraction['rel']['text'])
    for arg2 in extraction['arg2s']:
      arg2['text'] = sub(r"\((.*?)\)|\(|\)|\[|\]", r'', arg2['text'])
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


def write_article(args: str) -> None:
  [d_i, document, path] = args.split('\n')
  start = time()
  sentences = doc2sentences(document)
  output = ''
  for s_i, sentence in enumerate(sentences):
    output += f'S\t{d_i}\t{s_i}\t{sentence}\n'
    triples = extract_triple(sentence)['triples']
    for triple in triples:
      output += f'R\t{triple2sentence(triple)}\n'
    if len(triples) == 0:
      output += f'R\t{sentence}\n'
  with open(path, 'a', encoding='UTF8') as triplenote:
    triplenote.write(output)
  print(f'Article {int(d_i) + 1} Processed {(time() - start):.2f}sec')
