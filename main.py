import fire
from src.extract import extract,triple2sentence
from src.abstract import abstract
from src.rank import calculate_salient_scores
import spacy

nlp = spacy.load("en_core_web_sm")
def text(text: str):
  document = nlp(text)
  sentences = [sent.text for sent in document.sents]
  relation_triples = []
  index = 0
  for s in sentences:
    print(s)
    triples = extract(s)
    relation_triples.append([])
    for s1 in triples:
      relation_triples[index].append(s1)
    index += 1
  score_temp,sentence_temp,triple_temp = calculate_salient_scores(text, sentences, relation_triples, 0.5)
  temp_pairs = sorted(zip(score_temp,sentence_temp,triple_temp), reverse=True, key=lambda item:item[0])
  score,sentence_list,triple_list = zip(*temp_pairs)

  print("Top 3 Score")
  print("=========================================")
  for i in range(0,3):
    print(score[i])
  print("=========================================")
  
  print("Top 3 sentence")
  print("=========================================")
  for i in range(0,3):
    print(sentence_list[i])
  print("=========================================")

  print("Top 3 Triples")
  print("=========================================")
  for i in range(0,3):
    print(triple2sentence(triple_list[i]))
  print("=========================================")
  
  #top_triples = rank(triples)
  #return abstract(top_triples)


def file(file: str):
  document = open(file, 'r', encoding='UTF8').read()
  return text(document)


if __name__ == '__main__':
  fire.Fire()
