"""Day 3: Sweet Crumbs Home Bakery assistant using LangChain."""
from __future__ import annotations
import argparse
import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Any
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

MODEL = "openai/gpt-oss-20b"
TESTS = Path(__file__).with_name("tests.csv")

SYSTEM_V1 = """ROLE: Friendly assistant for Sweet Crumbs Home Bakery.
FACTS: Plum cake Rs 500; chocolate cake Rs 650; cupcake Rs 80 each.
Orders need 24 hours' notice. All cakes have eggless versions.
RULES: Never promise delivery time or place. If a fact is missing, say
"I'll check with the owner." Calculate totals carefully.
FORMAT: Under 50 words; friendly; reply in English or Telugu matching the customer."""

SYSTEM_V2 = """ROLE: Friendly assistant for Sweet Crumbs Home Bakery.
FACTS: Plum cake Rs 500; chocolate cake Rs 650; cupcake Rs 80 each.
Every cake can be made eggless. Every order requires at least 24 hours' notice.
RULES: Explain the 24-hour notice rule for earlier requests; never claim same-day
orders are possible. Never invent delivery coverage, delivery times, opening hours,
stock, or order confirmation. For missing business facts say:
"I'll check with the owner." Calculate totals carefully.
FORMAT: Under 50 words; friendly; reply in English or Telugu matching the customer."""

def get_price(item: str) -> float:
    """Return a listed bakery item's price in rupees; raise ValueError if unknown."""
    prices = {"plum cake": 500.0, "chocolate cake": 650.0, "cupcake": 80.0}
    try:
        return prices[item.strip().lower()]
    except KeyError:
        raise ValueError(f"{item!r} is not in the bakery menu.") from None

def has_24_hours_notice(order_time: datetime, requested_time: datetime) -> bool:
    """Return True if requested_time is at least 24 hours after order_time."""
    return (requested_time - order_time).total_seconds() >= 86400

def build_chain(temperature: float = 0.3, version: int = 2):
    """Build the LangChain prompt | Groq model | string parser pipeline."""
    if not os.getenv("GROQ_API_KEY"):
        raise EnvironmentError("Set GROQ_API_KEY before running model tasks.")
    llm = ChatGroq(model=MODEL, temperature=temperature)
    system = SYSTEM_V2 if version == 2 else SYSTEM_V1
    prompt = ChatPromptTemplate.from_messages([
        ("system", system), MessagesPlaceholder("history"), ("human", "{question}")
    ])
    return prompt | llm | StrOutputParser()

def load_tests():
    """Read the ten question/must-include cases from tests.csv."""
    with TESTS.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

def run_tests(chain: Any, label: str):
    """Run all CSV checks and return pass count, total and generated answers."""
    rows, passed, answers = load_tests(), 0, []
    print(f"\\n--- {label} ---")
    for i, row in enumerate(rows, 1):
        answer = chain.invoke({"history": [], "question": row["question"]})
        ok = row["must_include"].casefold() in answer.casefold()
        passed += int(ok)
        answers.append(answer)
        print(f"{'PASS' if ok else 'FAIL'} {i:02d} | {row['question']}")
        print(" Expected:", row["must_include"])
        print(" Answer:", answer)
    print(f"Pass rate: {passed}/{len(rows)} = {passed / len(rows):.1%}")
    return passed, len(rows), answers

def show_classification():
    """Classify three bakery jobs using the simplest suitable approach."""
    jobs = [
        ("Calculate total for 3 plum cakes", "Plain code", "Exact multiplication."),
        ("Write an Instagram caption for a new cake", "One LLM call", "One creative text response."),
        ("Understand an unclear order, check price and notice, prepare an order record",
         "Agent", "Requires decisions and multiple actions using tools; owner approval remains required."),
    ]
    print("\\n--- Agent or not? ---")
    for task, label, reason in jobs:
        print(f"{task} -> {label}: {reason}")

def compare_prompts():
    """Compare original and improved prompts on the same ten tests."""
    a = run_tests(build_chain(0.3, 1), "Prompt v1")
    b = run_tests(build_chain(0.3, 2), "Prompt v2")
    print(f"Prompt change: {a[0]}/{a[1]} -> {b[0]}/{b[1]} "
          f"({(b[0]/b[1]-a[0]/a[1])*100:+.1f} percentage points)")

def temperature_experiment():
    """Run tests twice at temperature 1.0 and count differing answers."""
    chain = build_chain(1.0, 2)
    first = run_tests(chain, "Temperature 1.0 – run 1")[2]
    second = run_tests(chain, "Temperature 1.0 – run 2")[2]
    changed = sum(x.strip() != y.strip() for x, y in zip(first, second))
    print(f"Answers that differed: {changed}/{len(first)}")
    print("Record the observed result; temperature can increase variation but does not guarantee it.")

def chat():
    """Run an interactive bakery chat with recent conversation history."""
    chain, history = build_chain(0.3, 2), []
    print("Sweet Crumbs assistant. Type exit to stop.")
    while True:
        q = input("You: ").strip()
        if q.lower() in {"exit", "quit", "bye"}:
            break
        if not q:
            continue
        answer = chain.invoke({"history": history[-16:], "question": q})
        print("Assistant:", answer)
        history.extend([("human", q), ("ai", answer)])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["all", "chat", "tests", "compare",
                        "temperature", "classification"], default="all")
    mode = parser.parse_args().mode
    print("2 plum cakes cost Rs", 2 * get_price("plum cake"))
    print("24-hour example:", has_24_hours_notice(
        datetime(2026, 11, 23, 10), datetime(2026, 11, 24, 10)))
    if mode == "classification":
        show_classification()
    elif mode == "chat":
        chat()
    elif mode == "tests":
        run_tests(build_chain(), "Prompt v2 tests")
    elif mode == "compare":
        compare_prompts()
    elif mode == "temperature":
        temperature_experiment()
    else:
        show_classification()
        compare_prompts()
        temperature_experiment()
        chat()

if __name__ == "__main__":
    main()
