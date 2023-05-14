import fire
from src.extract import extract
from src.rank import rank
from src.abstract import abstract
from src.train import training


def text(text: str) -> str:
  try:
    triples = extract(text)
  except Exception as e:
    print(e)
    return 'Too little information'
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
