from difflib import SequenceMatcher
import asyncio

import streamlit as st

from sjyyj.summary import summarize
from sjyyj.extract import triple2sentence


TITLE = 'RTSum: An Interpretable Summarizing Tool'
INITIAL = """The temperature of the planet’s oceans rose to new heights this week, setting a new record with no sign of cooling down.

The average global ocean surface temperature hit 20.96 degrees Celsius (69.7 Fahrenheit) at the end of July, according to modern data from the European Union’s Copernicus Climate Change Service, beating the previous record of 20.95 degrees Celsius set in 2016. The Copernicus ocean data goes back to 1979.

Scientists say the world needs to brace for ocean temperatures to keep rising as the arrival of El Niño – the natural climate fluctuation that originates in the tropical Pacific Ocean, and has a warming impact – layers on top of human-caused global warming.

Kaitlin Naughten, an oceanographer at British Antarctic Survey, said the data from Copernicus painted an alarming picture for the health of the oceans.

“Other datasets may give slightly different values – for example, [the US National Oceanic and Atmospheric Administration] is reporting that last April was still very slightly warmer than now,” she told CNN.

But what’s clear, she said, is “that current sea surface temperatures are exceptionally and unseasonably warm” and bringing wide-ranging implications, “especially for complex ecosystems such as coral reefs.”

Gregory C. Johnson, an oceanographer at NOAA, said sea surface temperatures have soared this year. “What we’re seeing is a massive increase. It’s about 15 years worth of the long term warming trend in a year,” he told CNN.

The heat could increase even further. Surface temperatures tend to remain high from August through to September before starting to decline, said Johnson. “There’s still room to have warmer sea surface temperatures” this year.

Some marine heat waves this year have particularly shocked scientists for just how unprecedented they are, and the damage they are causing. Ocean heat can lead to the mass bleaching of coral reefs, as well as the death of other marine life and increased sea level rise."""

st.set_page_config(page_title=TITLE)
st.header(TITLE)
st.markdown('''
### Copy & Paste ([CNN](https://edition.cnn.com/), [FoxNews](https://www.foxnews.com/)).
RTSum requires more than three lines of information. [Source Code](https://github.com/sjyyj/sjyyj), [Model](https://huggingface.co/sjyyj/sjyyj))
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


article = st.text_area("Text to summarize", INITIAL, height=400)


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
  phrases = list(filter(lambda p: len(p[0]) > 3, phrases))

  # Summary
  st.write("## Summary")
  st.markdown(
      f"<h6 style='padding: 0'>{response}</h6><hr style='margin: 1em 0px'>", unsafe_allow_html=True)

  # Highlight
  st.write("### Highlight")
  col1, col2 = st.columns(2)
  emphasis_sentence = col1.checkbox("**Sentence**", True)
  emphasis_phrase = col2.checkbox("**Phrases**", True)
  sentence_length = col1.slider(
      "Sentence highlight count", 0, len(sentences), 5)
  phrase_length = col2.slider(
      "Phrase highlight count", 0, len(phrases), 15)
  col1, col2, col3, col4, col5 = st.columns(5)
  emphasis_triple = col1.checkbox("**Triple**", True)
  emphasis_subject = col2.checkbox("(Subject)", emphasis_triple)
  emphasis_pred = col3.checkbox("(Predicate)", emphasis_triple)
  emphasis_object = col4.checkbox("(Object)", emphasis_triple)
  emphasis_adverbs = col5.checkbox("(Adverbs)", emphasis_triple)
  triple_length = st.slider("Triple highlight count", 0, len(triples), 7)

  # 1. Highlight Sentence
  html_article = article
  temp_article = article
  if emphasis_sentence:
    for i, sentence in enumerate(sentences[:sentence_length]):
      match = get_similar_part(temp_article, sentence["text"])
      temp_article = temp_article.replace(match, '', 1)

      if match:
        maximum = sentences[0]["score"]
        minimal = sentences[len(sentences) - 1]["score"]
        hexscore = hex(
            int(100 / (maximum - minimal) * (sentence["score"] - minimal)))[2:]
        background = f"background: #ffff00{hexscore}; padding: 0 2px"
        smallborder = "border-radius: 2px"
        position = "position: relative; left: 2px; top: 2px; padding: 0 1px"
        size = "font-size: 0.5rem"
        small = f"<span style='{size}; {background}; {smallborder}; {position}'>"

        border = "border-radius: 5px"
        html_sentence = sentence["text"].replace(
            match, f"<span style='{border}; {background}'>{match}</span>{small}S{i+1}</span>", 1)
        html_article = html_article.replace(sentence["text"], html_sentence, 1)

  # 2. Highlight Triple
  for i, triple in enumerate(triples[:triple_length]):
    if len(triple['extraction']['arg2s']) > 0:
      knowledge = triple2sentence(triple)
      match = get_similar_part(triple["parent"]["text"], knowledge)

      if match:
        maximum = triples[0]["score"]
        minimal = triples[len(triples) - 1]["score"]
        hexscore = hex(int(255 / (maximum - minimal) * (triple["score"] - minimal)))[2:]
        background = f"background: #bb3344{hexscore}; padding: 0 2px"
        color = f"color: #fff"
        black = f"color: #000"
        subcolor = f"background: #bbee00"
        border = "border-radius: 3px"
        smallborder = "border-radius: 2px"
        position = "position: relative; left: 2px; top: 2px; padding: 0 1px"
        size = "font-size: 0.5rem"
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

  # 3. Highlight Phrase
  if emphasis_phrase:
    maximum = phrases[0][1]
    minimal = phrases[len(phrases) - 1][1]
    for i, phrase in enumerate(phrases[:phrase_length]):
      match = get_similar_part(article, phrase[0].strip())

      if match:
        hexscore = hex(
            int(200 / (maximum - minimal) * (phrase[1] - minimal)))[2:]
        background = f"background: #33bb66{hexscore}; padding: 0 2px"
        smallborder = "border-radius: 2px"
        position = "position: relative; left: 2px; top: 2px; padding: 0 1px"
        size = "font-size: 0.5rem"
        small = f"<span style='{size}; {background}; {smallborder}; {position}'>"

        border = "border-radius: 5px"
        html_article = html_article.replace(
            match, f"<span style='{border}; {background}'>{match}</span>{small}P{i+1}</span>", 1)

  st.write(f"{html_article}", unsafe_allow_html=True)


if article:
  loop = asyncio.new_event_loop()
  loop.run_until_complete(main(article))
