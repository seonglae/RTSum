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


def exportarticle(path: str, output: str, start: int, end: int) -> None:
  with open(path, 'r', encoding='UTF8') as f:
    if start is None:
      start = 0
    if end is None:
      end = len(f)
    for i, line in enumerate(f):
      if int(i) < start:
        continue
      if start <= int(i) < end:
        write_article(f'{i}\n{line.strip()}\n{output}')
      else:
        break


def train(*, model="bert-base-cased", data='yelp_review_full', output='train') -> str:
  training(model, data, output)
  return ''


if __name__ == '__main__':
  fire.Fire()
