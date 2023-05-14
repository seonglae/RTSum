from src.extract import Triple, triple2sentence
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline


def abstract(triples: list[Triple], model_checkpoint: str, device: str = "cpu") -> str:
  # Load Model & Summarization Pipeline
  tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
  model = AutoModelForSeq2SeqLM.from_pretrained(model_checkpoint).to(device)
  summarizer = pipeline("summarization", model=model, tokenizer=tokenizer, device=device)

  # Make relation classes to a string
  relations = ' '.join(list(map(lambda triple: triple2sentence(triple, 10), triples)))
  if len(relations.split()) == 0: return

  # Make a summarization
  summary = summarizer(relations)[0]["summary_text"]
  return summary
