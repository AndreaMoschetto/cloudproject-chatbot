import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv


class Generator:
    def __init__(self):
        self._LLM_MODEL_NAME = "gemini-2.5-flash"
        load_dotenv()
        if "GOOGLE_API_KEY" not in os.environ:
            print("Error: GOOGLE_API_KEY not found in .env file.")
            exit()

        print(f"Loading LLM: {self._LLM_MODEL_NAME}")
        self.llm = ChatGoogleGenerativeAI(model=self._LLM_MODEL_NAME)

        self.prompt_template = ChatPromptTemplate.from_template(
            """
            You are an expert assistant. You must answer the user's question
            based *only* on the following context.
            If the context does not contain the answer, state that you don't know.
            Do not use any information outside of this context.

            CONTEXT:
            {context}

            USER'S QUESTION:
            {question}

            ANSWER:
            """
        )

    def generate_answer(self, query: str, context: str) -> str:
        formatted_prompt = self.prompt_template.format(
            context=context,
            question=query
        )
        print("Generating answer...")
        response = self.llm.invoke(formatted_prompt)
        return response.content
