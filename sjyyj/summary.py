import asyncio
from typing import Tuple, List
from time import time
from rouge_score import rouge_scorer

from sjyyj.extract import extract_triple, TripledSentence, doc2sentences, Triple
from sjyyj.abstract import abstract
from sjyyj.rank import rank


async def summarize(text: str) -> Tuple[str, List[TripledSentence], List[Triple], List[Tuple[str, float]]]:
  # Extract Sentences & Triples
  tripled_sentences: List[TripledSentence] = []
  try:
    start = time()
    sentences = doc2sentences(text)
    tripled_sentences = await asyncio.gather(
        *[extract_triple(sentence, 0.7) for sentence in sentences]
    )
    print(f"\nSplit takes time {time() - start} secs\n")
  except Exception as e:
    print(e)
    return 'Cannot extract summary', [], [], []

  # Abstraction
  start = time()
  sentence_rank, triple_rank, phrase_rank = rank(tripled_sentences)
  print(f"Rank takes time {time() - start} secs\n")
  if len(triple_rank) == 0:
    return text, [], [], []

  start = time()
  abstraction = abstract(triple_rank, 'sjyyj/sjyyj',
                         0), sentence_rank, triple_rank, phrase_rank
  print(f"Abstraction takes time {time() - start} secs\n")
  return abstraction


async def summarize_test(article: str, gold_summary: str):
  scorer = rouge_scorer.RougeScorer(
      ['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
  model_summary, _, _, _ = await summarize(article)
  scores = scorer.score(model_summary, gold_summary)
  print(f"""
Rouge-1: {scores['rouge1'].fmeasure}
Rouge-2: {scores['rouge2'].fmeasure}
Rouge-L: {scores['rougeL'].fmeasure}
Predict: {model_summary}
Gold: {gold_summary}
""")
  return scores
