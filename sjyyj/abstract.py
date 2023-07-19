from typing import List, Optional
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

from sjyyj.extract import Triple, triple2sentence


def abstract(triples: List[Triple], model_checkpoint: str = 'sjyyj/sjyyj', device: str | int = "cpu") -> str:
  # Load Model & Summarization Pipeline
  tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
  model = AutoModelForSeq2SeqLM.from_pretrained(model_checkpoint).to(device)
  summarizer = pipeline("summarization", model=model,
                        tokenizer=tokenizer, device=device)

  # Make relation classes to a string
  print(f"""
Score:{triples[0]['score']}, Confidence: {triples[0]['confidence']} - {triple2sentence(triples[0])}
Score:{triples[1]['score']}, Confidence: {triples[1]['confidence']} - {triple2sentence(triples[1])}
Score:{triples[2]['score']}, Confidence: {triples[2]['confidence']} - {triple2sentence(triples[2])}
""")
  relations = ''.join(list(map(tokenize_triple, triples[:3])))
  if len(relations.split()) == 0:
    return 'Cannot abstract triples'

  # Make a summarization
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
