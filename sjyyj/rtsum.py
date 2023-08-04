import torch
import torch.nn as nn

import networkx as nx
import spacy


class SRTExt(nn.Module):
  def __init__(self, aggtype='phsum'):
    super().__init__()
    self.nlp = spacy.load("en_core_web_sm")
    self.aggtype = aggtype

  def get_phrase_scores(self, sentences, relations, sentence_ids, topk=10):
    lemma_graph = nx.Graph()
    lemmas = {}

    for sentence_id, sentence in enumerate(sentences):
      candidate_relations = [(idx, relations[idx]) for idx in range(len(relations))
                             if sentence_ids[idx] == sentence_id]
      self._link_sentence(sentence, candidate_relations, lemma_graph, lemmas)

    ranks = nx.pagerank(lemma_graph)
    phrase_map = {key:ranks[node_id] for node_id, ((key, _),_) in enumerate(lemmas.items())}
    phrase_list = sorted(phrase_map.items(), key = lambda item: item[1], reverse=True)

    node_scores = []
    for node_id, ((_, _), relation_ids) in enumerate(lemmas.items()):
      node_scores.append(
          [ranks[node_id] if idx in relation_ids else 0 for idx in range(len(relations))])
    phrase_scores = torch.tensor(
        node_scores, dtype=torch.float64, device=sentence_ids.device)

    if self.aggtype == 'phsum':
      phrase_scores = phrase_scores.sum(dim=0)
    elif self.aggtype == 'phmean':
      phrase_scores = phrase_scores.sum(
          dim=0) / (phrase_scores != 0).sum(dim=0)
      phrase_scores[torch.isnan(phrase_scores)] = 0
    elif self.aggtype == 'phtopk':
      phrase_scores = torch.sort(
          phrase_scores, dim=0, descending=True)[0][:topk, :]
      phrase_scores = phrase_scores.sum(
          dim=0) / (phrase_scores != 0).sum(dim=0)
      phrase_scores[torch.isnan(phrase_scores)] = 0
    else:
      raise ValueError('Invalid Type for Phrase-Level Score Aggregation')

    return (phrase_scores - torch.mean(phrase_scores)) / torch.std(phrase_scores), phrase_list

  '''
    For phrase-level saliency score based on TextRank
    '''

  def _increment_edge(self, graph, node0, node1):
    if graph.has_edge(node0, node1):
      graph[node0][node1]["weight"] += 1.0
    else:
      graph.add_edge(node0, node1, weight=1.0)

  def _link_sentence(self, sentence, candidate_relations, lemma_graph, lemmas):
    visited_tokens = []
    visited_nodes = []

    for token in self.nlp(sentence):
      if token.pos_ in ["ADJ", "NOUN", "PROPN", "VERB"]:
        link_ids = [relation_id for relation_id,
                    relation in candidate_relations if token.text in relation]

        key = (token.lemma_, token.pos_)
        if key not in lemmas:
          lemmas[key] = set()
        lemmas[key].update(link_ids)

        node_id = list(lemmas.keys()).index(key)
        if not node_id in lemma_graph:
          lemma_graph.add_node(node_id)

        for prev_token in range(len(visited_tokens) - 1, -1, -1):
          if (token.i - visited_tokens[prev_token]) <= 3:
            self._increment_edge(lemma_graph, node_id,
                                 visited_nodes[prev_token])
          else:
            break

        visited_tokens.append(token.i)
        visited_nodes.append(node_id)
