from typing import List, Optional
from difflib import SequenceMatcher
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

from sjyyj.extract import Triple, triple2sentence


def abstract(triples: List[Triple], model_checkpoint: str, device: str | int = "cpu") -> str:
  # Load Model & Summarization Pipeline
  tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
  model = AutoModelForSeq2SeqLM.from_pretrained(model_checkpoint).to(device)
  summarizer = pipeline("summarization", model=model,
                        tokenizer=tokenizer, device=device)

  # Select top triples
  try:
    top_triples = triples[:3]
    matcher = SequenceMatcher(None, triple2sentence(
        triples[0]), triple2sentence(triples[1]))
    if matcher.ratio() > 0.8:
      top_triples = triples[:4]
    matcher = SequenceMatcher(None, triple2sentence(
        triples[1]), triple2sentence(triples[2]))
    if matcher.ratio() > 0.8:
      top_triples = triples[:5]
    matcher = SequenceMatcher(None, triple2sentence(
        triples[2]), triple2sentence(triples[3]))
    if matcher.ratio() > 0.8:
      top_triples = triples[:6]
    matcher = SequenceMatcher(None, triple2sentence(
        triples[3]), triple2sentence(triples[4]))
    if matcher.ratio() > 0.8:
      top_triples = triples[:7]

    print()
    for triple in top_triples:
      print(
          f"Score:{triple['score']}, Confidence: {triple['confidence']} - {triple2sentence(triple)}")
    print()
  except IndexError:
    return 'There is not enough information to make a summary.'

  # Make a summarization
  relations = ''.join(list(map(tokenize_triple, top_triples)))
  result = summarizer(relations)[0]
  summary = result["summary_text"]
  return summary


def tokenize_triple(
        triple: Triple, arg2max: Optional[int] = None, sub='<subject>', rel='<predicate>', obj='<object>'
) -> str:
  if arg2max is None:
    arg2max = len(triple['extraction']['arg2s'])
  return sub + triple['extraction']['arg1']['text'] + rel + triple['extraction']['rel']['text'] + obj + \
      ' '.join(
      list(map(lambda arg2: arg2['text'], triple['extraction']['arg2s']))[:arg2max])
