from src.extract import Triple, triple2sentence


def abstract(triple_rank: list[Triple]) -> str:
  return ' '.join(list(map(lambda triple: triple2sentence(triple), triple_rank[:3])))
