import fire

from sjyyj.summary import summarize, summarize_test
from sjyyj.extract import write_article
from sjyyj.dataset import extract2autotrain
from sjyyj.train import training


async def text(text: str) -> str:
  summary, _, _, _ = await summarize(text)
  return summary


async def file(path: str) -> str:
  with open(path, 'r', encoding='UTF8') as f:
    document = f.read()
  return await text(document)


async def test(article_file: str, summary_file: str, start: int, end: int) -> None:
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
          score = await summarize_test(article, gold_summary)
          mean_rouge1 += score['rouge1'].fmeasure
          mean_rouge2 += score['rouge2'].fmeasure
          mean_rouge_l += score['rougeL'].fmeasure
          print(f"""Mean
Rouge-1: {mean_rouge1 / (1 + int(i) - start)}
Rouge-2: {mean_rouge2 / (1 + int(i) - start)}
Rouge-L: {mean_rouge_l / (1 + int(i) - start)}""")
        else:
          break


async def exportarticle(path: str, output: str, start: int, end: int) -> None:
  with open(path, 'r', encoding='UTF8') as f:
    if start is None:
      start = 0
    if end is None:
      end = len(f)
    for i, line in enumerate(f):
      if int(i) < start:
        continue
      if start <= int(i) < end:
        return await write_article(f'{i}\n{line.strip()}\n{output}')
      else:
        break


def train(checkpoint='facebook/bart-large-cnn', owner='sjyyj', push=False,
          output='sentencification', dataset_id="sjyyj/autotrain-data-sjyyj"):
  training(checkpoint, owner, push, output, dataset_id)


def pushdata(path='data/cnn_dailymail/test/triple.txt', output='autotrain.csv') -> None:
  extract2autotrain(path, output)


if __name__ == '__main__':
  fire.Fire()
