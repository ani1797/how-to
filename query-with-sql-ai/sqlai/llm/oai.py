
from openai import AzureOpenAI


class AOAI():
    def __init__(self) -> None:
        self.client = AzureOpenAI()

    def completion(self, prompt: str) -> str:
        """Calls the OpenAI API to generate SQL queries.

        Args:
            prompt (str): Prompt to be sent to the API.

        Returns:
            str: SQL queries
        """
        return self.client.chat.completions.create(messages=[{"content": prompt, "role": "user"}], max_tokens=1000, stop=["\n\n"], model="gpt-35-turbo").choices[0].message.content
