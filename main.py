import fire
from os import getenv
from dotenv import load_dotenv
from spacy import load

from src.extract import extract, triple2sentence, Triple
from src.abstract import abstract
from src.train import training
from src.rank import rank


def text(text: str) -> str:
  # Extract Sentences & Triples
  load_dotenv()
  triples: list[Triple] = []
  try:
    # Split article to sentences
    nlp = load("en_core_web_sm")
    document = nlp(text)
    sentences = [sent.text for sent in document.sents]

    # Extract triples
    for sentence in sentences:
      triples += extract(sentence, getenv('OPENIE_URL'))
  except Exception as e:
    print(e)
    return 'Error'
  if len(triples) == 0:
    return 'Too little information'

  # Abstraction
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
