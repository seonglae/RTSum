import re
from difflib import SequenceMatcher

import streamlit as st
import torch

from sjyyj.summary import summarize
from sjyyj.extract import triple2sentence


TITLE = 'Three-line Summary'

st.set_page_config(page_title=TITLE)
st.header(TITLE)
st.markdown('''
### Copy & Paste ([CNN](https://edition.cnn.com/), [FoxNews](https://www.foxnews.com/)).
A three-line summary requires more than three lines of information. ([Usage Video](https://www.youtube.com/watch?v=fwk1Q-V5cro&t=350s), [Source Code](https://github.com/sjyyj/sjyyj), [Model](https://huggingface.co/sjyyj/sjyyj))
''', unsafe_allow_html=True)

styl = """
<style>
    .StatusWidget-enter-done{
      position: fixed;
      left: 50%;
      top: 50%;
      transform: translate(-50%, -50%);
    }
    .StatusWidget-enter-done button{
      display: none;
    }
</style>
"""
st.markdown(styl, unsafe_allow_html=True)


article = st.text_area("Text to summarize", height=400)


def get_similar_part(source, similar):
  matcher = SequenceMatcher(None, source, similar)
  matches = matcher.get_matching_blocks()
  if len(matches) > 1:
    return source[matches[0].a:matches[-2].a + matches[-2].size]
  return None


if article:
  print(f"Input: {article}")
  response, sentences, triples = summarize(article)
  html_article = article

  for sentence in sentences:
    match = get_similar_part(article, sentence["text"])

    if match:
      hexscore = hex(int(100 / sentences[0]["score"] * sentence["score"]))[2:]
      background = f"background: #3366bb{hexscore}"

      border = "border-radius: 5px"
      html_sentence = sentence["text"].replace(
          match, f"<span style='{border}; {background}'>{match}</span>")
      html_article = html_article.replace(sentence["text"], html_sentence)

  for triple in triples:
    if len(triple['extraction']['arg2s']) > 0:
      knowledge = triple2sentence(triple)
      article_sentence = get_similar_part(article, triple["sentence"])

      match = get_similar_part(article_sentence, knowledge)

      if match:
        hexscore = hex(int(255 / triples[0]["score"] * triple["score"]))[2:]
        background = f"background: #bb3344{hexscore}"

        border = "border-radius: 5px"
        html_sentence = article_sentence.replace(
            match, f"<span style='{border}; {background}'>{match}</span>")
        html_article = html_article.replace(article_sentence, html_sentence)

  st.write("## Summary")
  st.markdown(
      f"<h6 style='padding: 0'>{response}</h6>" +
      f"<hr style='margin: 1em 0px'>{html_article}", unsafe_allow_html=True)
