from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable


class SummarizationModel:
    SYSTEM_PROMPT = (
        "You will be provided with a text, and your task is to summarize it in a concise manner."
        "Please ensure that the summary captures the main points and is easy to understand."
        "Write a short summary in 3 sentences or less."
    )

    def __init__(self, model: BaseChatModel):
        self.model = model
        self.chain = (
            ChatPromptTemplate.from_messages(
                [
                    ("system", self.SYSTEM_PROMPT),
                    ("human", "{{text}}"),
                ],
                template_format="jinja2",
            )
            | self.model
            | StrOutputParser()
        )

    def train(self) -> Runnable:
        return self.chain
