from difflib import SequenceMatcher
import asyncio

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
    return source[matches[0].a:matches[-2].a + matches[-2].size]
  return None


async def main(article):
  print(f"Input: {article}")

  # Check Cache
  if article in st.session_state:
    print("Cache hit!")
    response, sentences, triples = st.session_state[article]
  else:
    response, sentences, triples = await summarize(article)
  st.session_state[article] = (response, sentences, triples)

  # Summary
  st.write("## Summary")
  st.markdown(
      f"<h6 style='padding: 0'>{response}</h6><hr style='margin: 1em 0px'>", unsafe_allow_html=True)

  # Highlight
  st.write("### Highlight")
  emphasis_sentence = st.checkbox("Sentence", False)
  col1, col2, col3, col4, col5 = st.columns(5)
  emphasis_triple = col1.checkbox("Triple", True)
  emphasis_subject = col2.checkbox("Subject", emphasis_triple)
  emphasis_pred = col3.checkbox("Predicate", emphasis_triple)
  emphasis_object = col4.checkbox("Object", emphasis_triple)
  emphasis_adverbs = col5.checkbox("Adverbs", emphasis_triple)

  html_article = article
  if emphasis_sentence:
    for sentence in sentences:
      match = get_similar_part(article, sentence["text"])

      if match:
        hexscore = hex(
            int(100 / sentences[0]["score"] * sentence["score"]))[2:]
        background = f"background: #3366bb{hexscore}; padding: 0 2px"

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
        background = f"background: #bb3344{hexscore}; padding: 0 2px"
        color = f"color: white"
        subcolor = f"background: #bbee00"
        border = "border-radius: 3px"
        smallborder = "border-radius: 2px"
        position = "position: relative; left: 2px; top: 2px; padding: 0 1px"
        size = "font-size: 3px"

        html_match = match
        if emphasis_subject:
          submatch = get_similar_part(
              match, triple["extraction"]["arg1"]["text"])
          html_match = html_match.replace(
              submatch, f"<span style='{border}; {background}; {color}'>{submatch}</span><span style='{size}; {subcolor}; {smallborder}; {position}'>S</span>")
        if emphasis_pred:
          submatch = get_similar_part(
              match, triple["extraction"]["rel"]["text"])
          html_match = html_match.replace(
              submatch, f"<span style='{border}; {background}; {color}'>{submatch}</span><span style='{size}; {subcolor}; {smallborder}; {position}'>P</span>")
        if emphasis_object:
          submatch = get_similar_part(
              match, triple["extraction"]["arg2s"][0]["text"])
          html_match = html_match.replace(
              submatch, f"<span style='{border}; {background}; {color}'>{submatch}</span><span style='{size}; {subcolor}; {smallborder}; {position}'>O</span>")

        if emphasis_subject or emphasis_pred or emphasis_object or emphasis_adverbs:
          html_article = html_article.replace(match, html_match)

  st.write(f"{html_article}", unsafe_allow_html=True)


if article:
  loop = asyncio.new_event_loop()
  loop.run_until_complete(main(article))
