from typing import List
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

from src.extract import Triple, triple2sentence


def abstract(triples: List[Triple], model_checkpoint: str = 'bert-base-uncased', device: str = "cpu") -> str:
  # Load Model & Summarization Pipeline
  tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
  model = AutoModelForSeq2SeqLM.from_pretrained(model_checkpoint).to(device)
  summarizer = pipeline("summarization", model=model,
                        tokenizer=tokenizer, device=device)

  # Make relation classes to a string
  relations = ' '.join(list(map(triple2sentence, triples)))
  if len(relations.split()) == 0:
    return 'Cannot abstract triples'

  # Make a summarization
  summary = summarizer(relations)[0]["summary_text"]
  return summary
