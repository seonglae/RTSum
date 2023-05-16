import fire
from os import getenv

from src.summary import summarize
from src.train import training


def text(text: str) -> str:
  summary, sentences, triples = summarize(text)
  return summary


def file(file: str) -> str:
  document = open(file, 'r', encoding='UTF8').read()
  return text(document)


def train(*, model="bert-base-cased", data='yelp_review_full', output='train') -> str:
  training(model, data, output)
  return ''


if __name__ == '__main__':
  fire.Fire()
