import streamlit as st
from streamlit_chat import message
from main import text


TITLE = '세줄요약좀'


st.set_page_config(page_title=TITLE)
st.header(TITLE)
st.markdown(
    "### 영문 뉴스를 입력하면 요약해주는 AI입니다 [Source Code](https://github.com/sjyyj/sjyyj)")

styl = f"""
<style>
    .stTextInput {{
      position: fixed;
      bottom: 3rem;
      z-index: 1;
    }}
</style>
"""
st.markdown(styl, unsafe_allow_html=True)

if 'generated' not in st.session_state:
  st.session_state['generated'] = []

if 'past' not in st.session_state:
  st.session_state['past'] = []


def query(input):
  response = text(input)
  return response


def get_text():
  input_text = st.text_input("You: ", key="input")
  return input_text


user_input = get_text()


if user_input:
  output = query(user_input)
  st.session_state.past.append(user_input)
  st.session_state.generated.append(output)


if st.session_state['generated']:
  for i in range(len(st.session_state['generated'])-1, -1, -1):
    message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
    message(st.session_state["generated"][i], key=str(i))
