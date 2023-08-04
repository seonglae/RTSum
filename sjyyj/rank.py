from typing import Tuple, List

from sentence_transformers import SentenceTransformer, util
import torch

from sjyyj.rtsum import SRTExt
from sjyyj.extract import TripledSentence, triple2sentence, Triple


def rank(
    tripled_sentences: List[TripledSentence], alpha=0.6, beta=3, gamma=0.5, model='thenlper/gte-large'
) -> Tuple[List[TripledSentence], List[Triple], List[Tuple[str, float]]]:
  print(f"alpha: {alpha}, beta: {beta}, gamma: {gamma}")
  model = SentenceTransformer(model)

  # 1. Compute Sentence Score
  sentences = list(
      map(lambda tripled_sentence: tripled_sentence['text'], tripled_sentences))
  embeddings = model.encode(sentences, convert_to_tensor=True)
  for i, tripled_sentence in enumerate(tripled_sentences):
    for j, _ in enumerate(tripled_sentences[i:]):  # Diagonal
      tripled_sentence['score'] += float(util.pytorch_cos_sim(embeddings[i],
                                                              embeddings[j]))

  # 2. Compute Triple Score
  triples: List[Triple] = []
  for tripled_sentence in tripled_sentences:
    triples += tripled_sentence['triples']
  if len(triples) == 0:
    return (tripled_sentences, [], [])
  triple_sentences = list(map(triple2sentence, triples))
  embeddings = model.encode(triple_sentences, convert_to_tensor=True)
  for i, triple in enumerate(triples):
    for j, _ in enumerate(triples):
      triple['score'] += float(util.pytorch_cos_sim(embeddings[i],
                                                    embeddings[j]))

  # 3. Compute Phrase Score
  rtsum = SRTExt()
  sentences_ids = torch.tensor(list(
      map(lambda triple: tripled_sentences.index(triple["parent"]), triples)))
  phrase_score, phrase_list = rtsum.get_phrase_scores(
      sentences, triple_sentences, sentences_ids)

  # Compute Final Triple Score
  for i, triple in enumerate(triples):
    triple['score'] = alpha * triple['parent']['score'] + beta * \
        triple['score'] + gamma * phrase_score[i]
  triples.sort(key=lambda triple: triple['score'], reverse=True)
  tripled_sentences.sort(key=lambda sentence: sentence['score'], reverse=True)

  if triple_sentences[0] in triple_sentences[1]:
    triple_sentences = triple_sentences[1:]
    triples = triples[1:]

  print(
      f"sentence: {len(tripled_sentences)}, triple: {len(triples)}, phrase: {len(phrase_list)}")
  return (tripled_sentences, triples, phrase_list)
