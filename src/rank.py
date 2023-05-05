from sentence_transformers import SentenceTransformer, util
from src.extract import Triple, triple2sentence


def rank(triples: list[Triple], model='sentence-transformers/all-MiniLM-L6-v2') -> list[Triple]:
  # Compute Embeddings
  model = SentenceTransformer(model)
  sentences = list(map(triple2sentence, triples))
  embeddings = model.encode(sentences, convert_to_tensor=True)
  scores: list[float] = []

  # Compute Similarity
  for i, _ in enumerate(sentences):
    scores.append(0)
    for j, _ in enumerate(sentences):
      scores[i] += float(util.pytorch_cos_sim(embeddings[i], embeddings[j]))
  scores.sort(reverse=True)
  threshold = scores[2] if len(scores) > 2 else 0

  # Select Top triples
  top_triples: list[Triple] = []
  top_triples.sort()
  for i, _ in enumerate(sentences):
    if scores[i] >= threshold:
      top_triples.append(triples[i])
  return top_triples
