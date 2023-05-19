from typing import Tuple, List

from src.extract import extract_triple, TripledSentence, doc2sentences, Triple
from src.abstract import abstract
from src.rank import rank


def summarize(text: str) -> Tuple[str, List[TripledSentence], List[Triple]]:
  # Extract Sentences & Triples
  tripled_sentences: List[TripledSentence] = []
  try:
    sentences = doc2sentences(text)
    for sentence in sentences:
      tripled_sentences.append(extract_triple(sentence))
  except Exception as e:
    print(e)
    return 'Cannot extract summary', [], []
  if len(tripled_sentences) == 0:
    return 'Cannot extract summary', [], []

  # Abstraction
  sentence_rank, triple_rank = rank(tripled_sentences)
  return abstract(triple_rank, 'Cynki/rtsum_abs_bart', 'cpu'), sentence_rank, triple_rank
