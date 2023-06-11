from typing import Tuple, List
from re import sub
from rouge_score import rouge_scorer

from src.extract import extract_triple, TripledSentence, doc2sentences, Triple
from src.abstract import abstract
from src.rank import rank


def summarize(text: str) -> Tuple[str, List[TripledSentence], List[Triple]]:
  # Extract Sentences & Triples
  tripled_sentences: List[TripledSentence] = []
  try:
    sentences = doc2sentences(text)
    for sentence in sentences:
      tripled_sentences.append(extract_triple(sentence, None, 0.7))
  except Exception as e:
    print(e)
    return 'Cannot extract summary', [], []

  # Abstraction
  sentence_rank, triple_rank = rank(tripled_sentences)
  if len(triple_rank) == 0:
    return text, [], []
  return abstract(triple_rank, 'Cynki/rtsum_abs_bart', 0), sentence_rank, triple_rank


def summarize_test(article: str, gold_summary: str):
  scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
  model_summary, _, _ = summarize(article)
  scores = scorer.score(model_summary, gold_summary)
  print(f"""
Rouge-1: {scores['rouge1'].fmeasure}
Rouge-2: {scores['rouge2'].fmeasure}
Rouge-L: {scores['rougeL'].fmeasure}
Predict: {model_summary}
Gold: {gold_summary}
""")
  return scores
