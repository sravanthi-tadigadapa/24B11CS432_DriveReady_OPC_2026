# Day 3 – Your First Agent: LangChain and Evaluation

## Business: Sweet Crumbs Home Bakery

This task adapts the Day 3 HTML tutorial to the Sweet Crumbs bakery. It rebuilds the assistant with LangChain, adds conversation history, evaluates ten customer questions, compares two prompt versions, runs a temperature experiment, classifies three business jobs, and prepares two typed Python functions for Day 4 tools.

## Files

```text
Day-3/
├── task.py
├── tests.csv
└── README.md
```

## Bakery facts

| Item / rule | Value |
|---|---:|
| Plum cake | Rs 500 |
| Chocolate cake | Rs 650 |
| Cupcake | Rs 80 |
| Order notice | At least 24 hours |
| Eggless cakes | Available |

The assistant must not invent delivery coverage, delivery times, opening hours, stock, or order confirmation. For missing business facts it says: "I'll check with the owner."

## Setup

Python 3.10+ recommended.

```bash
pip install -U langchain langchain-groq
```

Set your Groq key (never commit it to GitHub).

Windows PowerShell:
```powershell
$env:GROQ_API_KEY="your_groq_api_key"
```

macOS / Linux:
```bash
export GROQ_API_KEY="your_groq_api_key"
```

The code uses Groq model `openai/gpt-oss-20b`; confirm that it is available to your account.

## Run

```bash
python task.py
```

Choose one activity:

```bash
python task.py --mode classification
python task.py --mode tests
python task.py --mode compare
python task.py --mode temperature
python task.py --mode chat
```

- `classification`: prints three jobs labelled plain code, one LLM call, or agent.
- `tests`: runs the ten CSV evaluations using prompt v2 at temperature 0.3.
- `compare`: compares prompt v1 and improved prompt v2 using the same tests.
- `temperature`: runs the tests twice at temperature 1.0 and counts differing answers.
- `chat`: starts the interactive chatbot.
- Default `all`: runs classification, prompt comparison, temperature experiment, and chat.

## Day 3 requirements

### 1. Rewrite SYSTEM for your business
`SYSTEM_V1` and `SYSTEM_V2` are bakery-specific. V2 makes the 24-hour rule and missing-information behavior more explicit and prohibits unsupported delivery/opening-hours promises.

### 2. Ten customer tests
`tests.csv` contains ten customer questions and a `must_include` phrase for each. The program prints PASS/FAIL and calculates the actual pass rate from live model responses.

### 3. Prompt improvement
The compare mode runs the same questions against v1 and v2. Record whether the measured pass rate increased or decreased. Do not assume a result without running the API tests.

### 4. Temperature = 1.0
The temperature mode runs the same test set twice at 1.0 and reports how many full answers differ. Higher temperature can increase variation, but identical answers are possible.

### 5. Agent or not?

| Bakery job | Type | Reason |
|---|---|---|
| Calculate total for 3 plum cakes | Plain code | Exact multiplication |
| Write an Instagram caption | One LLM call | One creative text response |
| Understand unclear order, check price and notice, prepare an order record | Agent | Multi-step decisions and tool actions; owner approval is retained |

### 6. Two functions for Day 4

`task.py` includes:

- `get_price(item: str) -> float`: returns the listed menu price; raises `ValueError` for unknown items.
- `has_24_hours_notice(order_time: datetime, requested_time: datetime) -> bool`: checks whether at least 24 hours separate the order and requested times.

Both functions include type hints and docstrings.

## LangChain chain

The assistant uses:

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM),
    MessagesPlaceholder("history"),
    ("human", "{question}"),
])
chain = prompt | llm | StrOutputParser()
```

Conversation history is used in interactive chat. Evaluation cases use empty history so each question is tested independently.

## Record your actual results

Fill this table after running the experiments:

| Experiment | Your result |
|---|---|
| Prompt v1 | ___ / 10 = ___% |
| Prompt v2 | ___ / 10 = ___% |
| Pass-rate change | ___ percentage points |
| Temperature 1.0 answers that differed | ___ / 10 |
| Observation | ___ |

**Evaluation limitation:** `must_include` is a simple substring check, not a full quality or factuality evaluation. Review the generated answers manually as well.

## Notes

- API tests need internet access and a valid Groq API key.
- Model responses and pass rates may vary. No result is claimed until you run the tests.
- The Day 3 tutorial previews `create_agent` with no tools. Real tool-enabled agent behavior is the next day's task.
- Never upload API keys or private customer data to this public repository.
