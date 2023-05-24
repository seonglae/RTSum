from typing import Tuple, List
from sentence_transformers import SentenceTransformer, util

from src.extract import TripledSentence, triple2sentence, Triple


def rank(
    tripled_sentences: List[TripledSentence], alpha=0.6, beta=0.6, model='sentence-transformers/all-MiniLM-L6-v2'
) -> Tuple[List[TripledSentence], List[Triple]]:
  # Compute Embeddings
  model = SentenceTransformer(model)

  # Compute Sentence Similarity
  sentences = list(
      map(lambda tripled_sentence: tripled_sentence['text'], tripled_sentences))
  embeddings = model.encode(sentences, convert_to_tensor=True)
  for i, tripled_sentence in enumerate(tripled_sentences):
    # Diagonal Slice
    for j, _ in enumerate(tripled_sentences[i:]):
      tripled_sentence['score'] += float(util.pytorch_cos_sim(embeddings[i],
                                                        embeddings[j]))

  # Compute Triple Similarity
  triples: List[Triple] = []
  for tripled_sentence in tripled_sentences:
    triples += tripled_sentence['triples']
  if len(triples) == 0:
    return (tripled_sentences, [])
  triple_sentences = list(map(triple2sentence, triples))
  embeddings = model.encode(triple_sentences, convert_to_tensor=True)
  for i, triple in enumerate(triples):
    for j, _ in enumerate(triples[i:]):
      triple['score'] += float(util.pytorch_cos_sim(embeddings[i],
                                              embeddings[j]))

  # Compute Final Triple Score
  for triple in triples:
    triple['score'] = alpha * \
        triple['parent']['score'] + beta * triple['score']
  triples.sort(key=lambda triple: triple['score'], reverse=True)
  tripled_sentences.sort(
      key=lambda tripled_sentence: tripled_sentence['score'])
  return (tripled_sentences, triples)
