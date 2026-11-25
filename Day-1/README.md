# Sweet Crumbs Home Bakery Assistant

A small AI-powered customer support assistant built with **LangChain** and **Groq**. It answers customer questions using a bakery-specific system prompt.

## Features

- Uses Groq's `openai/gpt-oss-120b` chat model.
- Answers questions about Sweet Crumbs Home Bakery.
- Follows the business rules in the system prompt:
  - Cakes are baked to order.
  - Orders require 24 hours' notice.
  - Eggless versions are available for all cakes.
  - The assistant must not promise delivery times.
  - Replies should be polite and under 60 words.
- Runs as an interactive command-line program.

## Project files

```text
.
├── agenticAI_Day1.py
└── README.md
```

## Requirements

- Python 3.9 or newer
- A Groq API key

## Setup

### 1. Create and activate a virtual environment (recommended)

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\\Scripts\\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install langchain-groq
```

### 3. Set your Groq API key

Get an API key from the [Groq Console](https://console.groq.com/).

**Windows (PowerShell):**

```powershell
$env:GROQ_API_KEY="your_groq_api_key"
```

**macOS / Linux:**

```bash
export GROQ_API_KEY="your_groq_api_key"
```

Keep your API key private. Do not hard-code it in the Python file or commit it to GitHub.

### 4. Run the application

```bash
python agenticAI_Day1.py
```

Ask a question, for example:

```text
You: Can I get my order tomorrow?
```

Enter `exit` or `quit` to close the program.

## How it works

1. The program reads `GROQ_API_KEY` from the environment.
2. It initializes the Groq model through LangChain's `ChatGroq`.
3. The `SYSTEM` prompt provides the bakery's facts and response rules.
4. The `ask()` function sends the system prompt and customer's question to the model.
5. The response is printed in the terminal.

## Notes

- The original notebook used Google Colab Secrets (`userdata.get("GROQ_API_KEY")`). This `.py` version uses an environment variable so it can run locally.
- The notebook also included a separate Groq Prompt Guard model example. The main Python application above focuses on the bakery assistant workflow; it does not run that separate demonstration.
- Model availability and naming can change. If Groq reports that the configured model is unavailable, replace `MODEL` in the Python file with a currently supported chat model in your Groq account.

## Example

A customer asking whether an order can be placed for tomorrow should be reminded that orders need 24 hours' notice. The assistant should not guarantee a delivery time.
