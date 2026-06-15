import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st
from llm.oai import AOAI
from llm.ollama import Ollama
from tools.sqlprocessor import SQL

if "message" not in st.session_state:
    st.session_state.message = []

if "model_selection" not in st.session_state:
    st.session_state.model_selection = "Azure OpenAI"

for message in st.session_state.message:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
    elif message["role"] == "assistant":
        with st.chat_message("user"):
            if message["df"] is not None:
                st.dataframe(message["df"])
            elif message["content"]:
                st.markdown("assistant", message["content"])
    else:
        raise ValueError(f"Invalid message type: {message['type']}")

ai = AOAI()
dd = Path("data_dictionary.csv").read_text()
sql = SQL(dd, "sqlite3", ai.completion, sqlite3.connect("falcon.sqlite"))


def swap_model():
    global ai, sql, dd
    print(f"Swapping model to {st.session_state.model_selection}")
    if st.session_state.model_selection == "Azure OpenAI":
        ai = AOAI()
        sql = SQL(dd, "sqlite3", ai.completion, sqlite3.connect("falcon.sqlite"))
    elif st.session_state.model_selection == "Local AI":
        ai = Ollama("https://ollama.docker.localhost")
        sql = SQL(dd, "sqlite3", ai.completion, sqlite3.connect("falcon.sqlite"))
    else:
        raise ValueError(f"Invalid model selection: {st.session_state.model_selection}")


def natural_language_answer(df: pd.DataFrame, question: str):
    table = df.to_markdown()
    from jinja2 import Template

    template = Template(Path("prompts/nl_answer.jinja2").read_text())
    prompt = template.render(context=table, question=question)
    return ai.completion(prompt)


def main():
    st.sidebar.title("SQL Assistant")
    st.sidebar.selectbox(
        "Select the AI you would like to use",
        ["Azure OpenAI", "Local AI"],
        index=0,
        key="model_selection",
        on_change=swap_model,
    )

    question = st.chat_input("What would you like to know?")
    if question:
        with st.chat_message("user"):
            st.markdown(question)
            st.session_state.message.append({"role": "user", "content": question})
        with st.spinner("Thinking..."):
            try:
                answer_df = sql.ask(question, max_retry=3)
                with st.chat_message("assistant"):
                    st.dataframe(answer_df)
                    # answer = natural_language_answer(answer_df, question)
                    # st.markdown(answer)
                    st.session_state.message.append(
                        {"role": "assistant", "df": answer_df}
                    )
            except pd.errors.DatabaseError as e:
                print(e)
                with st.chat_message("assistant"):
                    st.markdown(
                        "I'm sorry, I ran into an issue executing your query. Please see logs for more details."
                    )
                    st.session_state.message.append(
                        {
                            "role": "assistant",
                            "content": "I'm sorry, I ran into an issue executing your query. Please see logs for more details.",
                        }
                    )


if __name__ == "__main__":
    main()
