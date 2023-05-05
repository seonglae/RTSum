from src.extract import Triple, triple2sentence


def abstract(triples: list[Triple]) -> str:
  return ' '.join(list(map(lambda triple: triple2sentence(triple, 10), triples)))
