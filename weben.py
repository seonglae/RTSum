import streamlit as st
from streamlit_chat import message
from src.summary import summarize


TITLE = 'Three-line Summary'


st.set_page_config(page_title=TITLE)
st.header(TITLE)
st.markdown('''
### Copy & Paste ([CNN](https://edition.cnn.com/), [FoxNews](https://www.foxnews.com/)).
A three-line summary requires more than three lines of information. ([Usage Video](https://www.youtube.com/watch?v=fwk1Q-V5cro&t=350s), [Source Code](https://github.com/sjyyj/sjyyj), [Model](https://huggingface.co/sjyyj/sjyyj))
''', unsafe_allow_html=True)

styl = f"""
<style>
    .stTextInput {{
      position: fixed;
      bottom: 3rem;
      z-index: 1;
    }}
    .StatusWidget-enter-done{{
      position: fixed;
      left: 50%;
      top: 50%;
      transform: translate(-50%, -50%);
    }}
    .StatusWidget-enter-done button{{
      display: none;
    }}
</style>
"""
st.markdown(styl, unsafe_allow_html=True)

if 'generated' not in st.session_state:
  st.session_state['generated'] = []

if 'past' not in st.session_state:
  st.session_state['past'] = []


def query(input):
  response, sentences, triples = summarize(input)
  return response


def get_text():
  input_text = st.text_input("You: ", key="input")
  return input_text


user_input = get_text()


if user_input:
  output = query(user_input)
  st.session_state.past.append(user_input)
  st.session_state.generated.append('Summary: ' + output)


if st.session_state['generated']:
  for i, _ in enumerate(st.session_state['generated']):
    message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
    message(st.session_state["generated"][i], key=str(i), seed=13)
