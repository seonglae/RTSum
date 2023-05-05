import fire
from src.extract import extract
from src.rank import rank
from src.abstract import abstract


def text(text: str):
  triples = extract(text)
  top_triples = rank(triples)
  return abstract(top_triples)


def file(file: str):
  document = open(file, 'r', encoding='UTF8').read()
  return text(document)


if __name__ == '__main__':
  fire.Fire()
