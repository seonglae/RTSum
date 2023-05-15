from sentence_transformers import SentenceTransformer, util
from src.extract import Triple, triple2sentence
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


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


def cosine_similarity_sentences(original_text, extracted_sentence):
  vectorizer = TfidfVectorizer()
  tfidf_matrix = vectorizer.fit_transform([original_text, extracted_sentence])
  return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0][0]


def cosine_similarity_relation_triples_list(original_text, extracted_relation_triples_list):
  relation_similarities = []
  for relation_triples in extracted_relation_triples_list:
    relation_sentence = triple2sentence(relation_triples)
    similarity = cosine_similarity_sentences(original_text, relation_sentence)
    relation_similarities.append(similarity)
  return relation_similarities


def calculate_salient_scores(original_text, sentences, relation_triples_list, a):
  scores = []
  Sr_list_return = []
  Ss_list_return = []
  for sentence, relation_triples in zip(sentences, relation_triples_list):
    Sr_list = cosine_similarity_relation_triples_list(
        original_text, relation_triples)
    Ss = cosine_similarity_sentences(original_text, sentence)
    if (len(Sr_list) == 0):
      St = a*Ss
      Sr_list_return.append(["없음"])
    else:
      St = max(Sr_list) + a*Ss
      Sr_list_return.append(relation_triples[Sr_list.index(max(Sr_list))])
    Ss_list_return.append(sentence)
    scores.append(St)
  return scores, Ss_list_return, Sr_list_return
