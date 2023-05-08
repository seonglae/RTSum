from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
import numpy as np
import evaluate


def training(model: str, data: str, output: str):
  # Load Dataset
  dataset = load_dataset(data)
  tokenized_datasets = dataset.map(generate_tokenizer(model), batched=True)
  small_train_dataset = tokenized_datasets["train"].shuffle(
      seed=42).select(range(1000))
  small_eval_dataset = tokenized_datasets["test"].shuffle(
      seed=42).select(range(1000))

  # Train
  training_args = TrainingArguments(
      output_dir=output, evaluation_strategy="epoch")
  model = AutoModelForSequenceClassification.from_pretrained(
      model, num_labels=5)
  trainer = Trainer(
      model=model,
      args=training_args,
      train_dataset=small_train_dataset,
      eval_dataset=small_eval_dataset,
      compute_metrics=generate_compute_metrics(),
  )
  trainer.train()


def generate_tokenizer(model: str):
  tokenizer = AutoTokenizer.from_pretrained(model)

  def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True)
  return tokenize_function


def generate_compute_metrics():
  metric = evaluate.load("accuracy")

  def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return metric.compute(predictions=predictions, references=labels)
  return compute_metrics


def test():
  return


def push():
  return
