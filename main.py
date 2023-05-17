from multiprocessing import Pool
from typing import List, cast
from os import cpu_count

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
  cpu = cast(int, cpu_count())
  with open(path, 'r', encoding='UTF8') as f:
    with Pool(int(cpu / 2)) as pool:
      args: List[str] = []
      for i, line in enumerate(f):
        args.append(f'{i}\n{line.strip()}\n{output}')
      pool.map(write_article, args)
      pool.close()
      pool.join()


def train(*, model="bert-base-cased", data='yelp_review_full', output='train') -> str:
  training(model, data, output)
  return ''


if __name__ == '__main__':
  fire.Fire()
