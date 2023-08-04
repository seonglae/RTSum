from difflib import SequenceMatcher
import asyncio
import re

import streamlit as st

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
    return source[matches[0].a:matches[-2].a + matches[-2].size].strip()
  return None


async def main(article: str):
  # Check Cache
  if article in st.session_state:
    print("Cache hit!")
    response, sentences, triples, phrases = st.session_state[article]
  else:
    print(f"Input: {article}")
    response, sentences, triples, phrases = await summarize(article)
    print(f"Output: {response}")
  st.session_state[article] = (response, sentences, triples, phrases)

  # Summary
  st.write("## Summary")
  st.markdown(
      f"<h6 style='padding: 0'>{response}</h6><hr style='margin: 1em 0px'>", unsafe_allow_html=True)

  # Highlight
  st.write("### Highlight")
  col1, col2 = st.columns(2)
  emphasis_sentence = col1.checkbox("**Sentence**", False)
  emphasis_phrase = col2.checkbox("**Phrases**", False)
  col1, col2, col3, col4, col5 = st.columns(5)
  emphasis_triple = col1.checkbox("**Triple**", True)
  emphasis_subject = col2.checkbox("(Subject)", emphasis_triple)
  emphasis_pred = col3.checkbox("(Predicate)", emphasis_triple)
  emphasis_object = col4.checkbox("(Object)", emphasis_triple)
  emphasis_adverbs = col5.checkbox("(Adverbs)", emphasis_triple)

  # 1. Highlight Sentence
  html_article = article
  temp_article = article
  if emphasis_sentence:
    for i, sentence in enumerate(sentences):
      match = get_similar_part(temp_article, sentence["text"])
      temp_article = temp_article.replace(match, '', 1)

      if match:
        hexscore = hex(
            int(100 / sentences[0]["score"] * sentence["score"]))[2:]
        background = f"background: #3366bb{hexscore}; padding: 0 2px"
        smallborder = "border-radius: 2px"
        position = "position: relative; left: 2px; top: 2px; padding: 0 1px"
        size = "font-size: 3px"
        small = f"<span style='{size}; {background}; {smallborder}; {position}'>"

        border = "border-radius: 5px"
        html_sentence = sentence["text"].replace(
            match, f"<span style='{border}; {background}'>{match}</span>{small}S{i+1}</span>", 1)
        html_article = html_article.replace(sentence["text"], html_sentence, 1)

  # 2. Highlight Triple
  for i, triple in enumerate(triples):
    if len(triple['extraction']['arg2s']) > 0:
      knowledge = triple2sentence(triple)
      match = get_similar_part(triple["parent"]["text"], knowledge)

      if match:
        hexscore = hex(int(255 / triples[0]["score"] * triple["score"]))[2:]
        background = f"background: #bb3344{hexscore}; padding: 0 2px"
        color = f"color: white"
        black = f"color: black"
        subcolor = f"background: #bbee00"
        border = "border-radius: 3px"
        smallborder = "border-radius: 2px"
        position = "position: relative; left: 2px; top: 2px; padding: 0 1px"
        size = "font-size: 3px"
        small = f"<span style='{size}; {black}; {subcolor}; {smallborder}; {position}'>"

        html_match = match
        temp_match = triple["parent"]["text"]
        if emphasis_subject:
          submatch = get_similar_part(
              temp_match, triple["extraction"]["arg1"]["text"])
          html_match = html_match.replace(
              submatch, f"<span style='{border}; {background}; {color}'>{submatch}</span>{small}S{i+1}</span>", 1)
        if emphasis_pred:
          submatch = get_similar_part(
              temp_match, triple["extraction"]["rel"]["text"])
          html_match = html_match.replace(
              submatch, f"<span style='{border}; {background}; {color}'>{submatch}</span>{small}P{i+1}</span>", 1)
        if emphasis_object:
          submatch = get_similar_part(
              temp_match, triple["extraction"]["arg2s"][0]["text"])
          html_match = html_match.replace(
              submatch, f"<span style='{border}; {background}; {color}'>{submatch}</span>{small}O{i+1}</span>", 1)
        if emphasis_adverbs and len(triple["extraction"]["arg2s"]) > 1:
          for adverb in triple["extraction"]["arg2s"][1:]:
            if len(adverb["text"].strip().split(' ')) > 1:
              submatch = get_similar_part(
                  temp_match, adverb["text"])
              html_match = html_match.replace(
                  submatch, f"<span style='{border}; {background}; {color}'>{submatch}</span>{small}A{i+1}</span>", 1)

        if emphasis_subject or emphasis_pred or emphasis_object or emphasis_adverbs:
          html_article = html_article.replace(match, html_match, 1)

  # 2. Highlight Phrase
  if emphasis_phrase:
    maximum = phrases[0][1]
    minimal = phrases[len(phrases) - 1][1]
    for i, phrase in enumerate(list(filter(lambda p: len(p[0]) > 3, phrases))[:10]):
      match = get_similar_part(article, phrase[0].strip())

      if match:
        hexscore = hex(
            int(100 / (maximum - minimal) * phrase[1]))[2:]
        background = f"background: #33bb66{hexscore}; padding: 0 2px"
        smallborder = "border-radius: 2px"
        position = "position: relative; left: 2px; top: 2px; padding: 0 1px"
        size = "font-size: 3px"
        small = f"<span style='{size}; {background}; {smallborder}; {position}'>"

        border = "border-radius: 5px"
        html_article = html_article.replace(
            match, f"<span style='{border}; {background}'>{match}</span>{small}P{i+1}</span>", 1)

  st.write(f"{html_article}", unsafe_allow_html=True)


if article:
  loop = asyncio.new_event_loop()
  loop.run_until_complete(main(article))
