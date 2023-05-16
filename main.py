from asyncio import wait
from typing import Coroutine

import fire

from src.summary import summarize
from src.train import training
from src.extract import write_article


def text(text: str) -> str:
  summary, _, _ = summarize(text)
  return summary


def file(path: str) -> str:
  with open(path, 'r', encoding='UTF8') as f:
    document = f.read()
  return text(document)


async def exportarticle(path: str, output: str) -> None:
  with open(path, 'r', encoding='UTF8') as f:
    routines: list[Coroutine] = []
    for d_i, document in enumerate(f):
      routines.append(write_article(output, document, d_i))
    await wait(routines)


def train(*, model="bert-base-cased", data='yelp_review_full', output='train') -> str:
  training(model, data, output)
  return ''


if __name__ == '__main__':
  fire.Fire()
