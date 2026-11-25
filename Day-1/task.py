"""Sweet Crumbs Home Bakery assistant using Groq + LangChain.

Set GROQ_API_KEY in your environment before running this script.
"""
import os
from langchain_groq import ChatGroq

SYSTEM = """You are the assistant for Sweet Crumbs Home Bakery.
Facts: we bake to order; orders need 24 hours' notice; all cakes have eggless versions.
Rules: never promise delivery times; if you do not know, say so.
Format: reply politely in under 60 words."""

MODEL = "openai/gpt-oss-120b"


def create_assistant():
    """Initialize the Groq chat model."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Set it as an environment variable first."
        )

    return ChatGroq(
        model=MODEL,
        temperature=0,
        groq_api_key=api_key,
    )


def ask(llm, question: str) -> str:
    """Ask the bakery assistant a question and return its response."""
    return llm.invoke(
        [("system", SYSTEM), ("human", question)]
    ).content


def main():
    llm = create_assistant()
    print("Sweet Crumbs Home Bakery Assistant")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("You: ").strip()
        if question.lower() in {"exit", "quit"}:
            print("Assistant: Thank you for contacting Sweet Crumbs!")
            break
        if not question:
            continue

        try:
            print(f"Assistant: {ask(llm, question)}\n")
        except Exception as exc:
            print(f"Error while contacting Groq: {exc}\n")


if __name__ == "__main__":
    main()
