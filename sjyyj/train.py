from datasets import load_dataset, splits, Dataset
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from transformers import Seq2SeqTrainingArguments, Seq2SeqTrainer, DataCollatorForSeq2Seq
import numpy as np
import evaluate
import torch


def preprocesser(tokenizer):
  def preprocess_function(examples):
    inputs = [doc for doc in examples["text"]]
    model_inputs = tokenizer(inputs, max_length=1024, truncation=True)
    labels = tokenizer(
        text_target=examples["target"], max_length=128, truncation=True)
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs
  return preprocess_function


def metric_function(tokenizer, metric):
  def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    decoded_preds = tokenizer.batch_decode(
        predictions, skip_special_tokens=True)
    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)
    result = metric.compute(predictions=decoded_preds,
                            references=decoded_labels, use_stemmer=True)
    prediction_lens = [np.count_nonzero(
        pred != tokenizer.pad_token_id) for pred in predictions]
    result["gen_len"] = np.mean(prediction_lens)
    return {k: round(v, 4) for k, v in result.items()}
  return compute_metrics


def training(checkpoint, owner, push, output, dataset_id):
  # Load model
  tokenizer = AutoTokenizer.from_pretrained(checkpoint)
  tokenizer.add_tokens(['<subject>', '<predicate>', '<object>'])

  # Load dataset
  dataset = load_dataset(dataset_id, split='train')
  splited_dataset = dataset.train_test_split(test_size=0.2)
  tokenized_dataset = splited_dataset.map(
      preprocesser(tokenizer), batched=True)
  print(tokenized_dataset["train"][0])

  # Train
  model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint)
  data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=checkpoint)
  training_args = Seq2SeqTrainingArguments(
      output_dir=output,
      evaluation_strategy="epoch",
      learning_rate=2e-5,
      per_device_train_batch_size=8,
      per_device_eval_batch_size=8,
      weight_decay=0.01,
      save_total_limit=3,
      num_train_epochs=4,
      predict_with_generate=True,
      fp16=torch.cuda.is_available(),
      push_to_hub=True,
  )
  trainer = Seq2SeqTrainer(
      model=model,
      args=training_args,
      train_dataset=tokenized_dataset["train"],
      eval_dataset=tokenized_dataset["test"],
      tokenizer=tokenizer,
      data_collator=data_collator,
      compute_metrics=metric_function(tokenizer, evaluate.load("rouge")),
  )
  trainer.train()

  # Push
  if push:
    tokenizer.push_to_hub(f"{owner}/{output}", use_auth_token=True)
    model.push_to_hub(f"{owner}/{output}", use_auth_token=True)
