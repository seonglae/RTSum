import fire

from src.summary import summarize, summarize_test
from src.extract import write_article


def text(text: str) -> str:
  summary, _, _ = summarize(text)
  return summary


def file(path: str) -> str:
  with open(path, 'r', encoding='UTF8') as f:
    document = f.read()
  return text(document)


def test(article_file: str, summary_file: str, start: int, end: int) -> str:
  with open(article_file, 'r', encoding='UTF8') as articles:
    with open(summary_file, 'r', encoding='UTF8') as summaries:
      if start is None:
        start = 0
      if end is None:
        end = len(articles)
      gold_summaries = summaries.readlines()
      mean_rouge1 = 0
      mean_rouge2 = 0
      mean_rouge_l = 0
      for i, article in enumerate(articles):
        if int(i) < start:
          continue
        if start <= int(i) < end:
          target_lines = filter(lambda line: int(
              line.split('\t')[0]) == i, gold_summaries)
          gold_summary = ' '.join([line.split('\t')[2].strip()
                                  for line in target_lines])
          score = summarize_test(article, gold_summary)
          mean_rouge1 += score['rouge1'].fmeasure
          mean_rouge2 += score['rouge2'].fmeasure
          mean_rouge_l += score['rougeL'].fmeasure
        else:
          break
      return f"""Results
      Rouge-1: {mean_rouge1 / (end - start)}
      Rouge-2: {mean_rouge2 / (end - start)}
      Rouge-L: {mean_rouge_l / (end - start)}
      """


def exportarticle(path: str, output: str, start: int, end: int) -> None:
  with open(path, 'r', encoding='UTF8') as f:
    if start is None:
      start = 0
    if end is None:
      end = len(f)
    for i, line in enumerate(f):
      if int(i) < start:
        continue
      if start <= int(i) < end:
        write_article(f'{i}\n{line.strip()}\n{output}')
      else:
        break


if __name__ == '__main__':
  fire.Fire()
