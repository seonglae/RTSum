import fire
from os import getenv
from dotenv import load_dotenv

from src.extract import extract, triple2sentence
from src.abstract import abstract
from src.train import training
from src.rank import rank


def text(text: str) -> str:
  load_dotenv()
  try:
    triples = extract(text, getenv('OPENIE_URL'))
  except Exception as e:
    print(e)
    return 'Error'
  if len(triples) == 0:
    return 'Too little information'
  top_triples = rank(triples)
  return abstract(top_triples)


def file(file: str) -> str:
  document = open(file, 'r', encoding='UTF8').read()
  return text(document)


def train(*, model="bert-base-cased", data='yelp_review_full', output='train') -> str:
  training(model, data, output)
  return ''


if __name__ == '__main__':
  fire.Fire()
