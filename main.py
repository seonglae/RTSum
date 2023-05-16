from time import time

import fire

from src.summary import summarize
from src.train import training
from src.extract import doc2sentences, extract_triple, triple2sentence


def text(text: str) -> str:
  summary, _, _ = summarize(text)
  return summary


def file(path: str) -> str:
  with open(path, 'r', encoding='UTF8') as f:
    document = f.read()
  return text(document)


def exportarticle(path: str, output: str) -> None:
  with open(output, 'w', encoding='UTF8') as triplenote:
    with open(path, 'r', encoding='UTF8') as f:
      for d_i, document in enumerate(f):
        start = time()
        sentences = doc2sentences(document)
        for s_i, sentence in enumerate(sentences):
          triplenote.write(f'S\t{d_i}\t{s_i}\t{sentence}\n')
          triples = extract_triple(sentence)['triples']
          for triple in triples:
            triplenote.write(f'R\t{triple2sentence(triple)}\n')
          if len(triples) == 0:
            triplenote.write(f'R\t{sentence}\n')
        print(f'Article {d_i + 1} Processed {(time() - start):.2f}sec')


def train(*, model="bert-base-cased", data='yelp_review_full', output='train') -> str:
  training(model, data, output)
  return ''


if __name__ == '__main__':
  fire.Fire()
