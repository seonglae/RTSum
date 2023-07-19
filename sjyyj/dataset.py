from datasets import Dataset


def extract2autotrain(path, output, dataset_id="sjyyj/autotrain-data-sjyyj"):
  def generator():
    with open(path, mode="r", encoding='utf-8') as f:
      lines = f.readlines()
      triples = []
      for line in lines:
        tokens = line.split('\t')
        if tokens[0] == 'S':
          if len(triples) > 0:
            text = ''
            for triple in triples:
              text += f"<subject>{triple[0]}<predicate>{triple[1]}<object>{' '.join(triple[2:])}"
            yield {"text": text.strip(), "target": sentence.strip()}
            triple = ''
          triples = []
          sentence = ' '.join(tokens[3:])
        elif tokens[0] == 'R':
          triples.append(tokens[1:])
  dataset = Dataset.from_generator(generator)
  dataset.to_csv(output)
  dataset.push_to_hub(dataset_id)
  return dataset
