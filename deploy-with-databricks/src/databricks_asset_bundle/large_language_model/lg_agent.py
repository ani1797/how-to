from langchain_core.language_models import BaseChatModel
from langchain_core.tools import tool
from langchain_openai import AzureChatOpenAI
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import create_react_agent

from databricks_asset_bundle.large_language_model.lc_model import SummarizationModel


@tool
def summarize(text: str) -> str:
    """Summarize the text using an LLM model specializing in summarization.

    Args:
        text (str): The text to summarize.

    Returns:
        str: The summarized text.
    """
    model = SummarizationModel(AzureChatOpenAI(azure_deployment="gpt-4.1-nano"))
    chain = model.train()
    return chain.invoke({"text": text})


class GeneralAgent:
    def __init__(self, llm, debug: bool = False):
        self.llm = llm
        self.agent = create_react_agent(llm, tools=[summarize], debug=debug)

    def train(self):
        return self.agent


def create_agent(llm: BaseChatModel) -> CompiledStateGraph:
    """Create a general-purpose agent using the provided LLM.

    Args:
        llm (BaseChatModel): The language model to use for the agent.

    Returns:
        CompiledStateGraph: The compiled state graph representing the agent.
    """
    return GeneralAgent(llm).train()
