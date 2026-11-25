
import json
import functools
from openai import RateLimitError, APIConnectionError, AuthenticationError

# 1. MODEL CONFIGURATION
MODEL = "openai/gpt-oss-20b"

# 2. BAKERY MENU (DICTIONARY)
MENU = {
    "plum cake": 500,
    "chocolate cake": 650,
    "cupcake": 80
}

# 3. SYSTEM PROMPT
SYSTEM = f"""
ROLE:
You are a friendly assistant for Sweet Crumbs Home Bakery.

FACTS:
Menu and prices in rupees: {json.dumps(MENU)}
Orders need 24 hours' notice.
All cakes have eggless versions.

RULES:
Never promise a delivery time.
If information is unavailable, say
"I'll check with the owner."

FORMAT:
Keep replies under 50 words.
Be friendly.
Reply in English or Telugu based on the customer.

Remember the customer's name and order during the chat.
"""

# 4. FEW-SHOT EXAMPLES
EXAMPLES = [
    {"role": "user", "content": "I need 2 plum cakes"},
    {"role": "assistant", "content": "order"},

    {"role": "user", "content": "Do you have eggless cakes?"},
    {"role": "assistant", "content": "question"},

    {"role": "user", "content": "The cake was dry"},
    {"role": "assistant", "content": "complaint"}
]

# 5. DECORATOR
def log_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[LOG] Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"[LOG] Result: {result}")
        return result
    return wrapper

# 6. PRICE CALCULATION FUNCTION
@log_call
def get_price(item: str, qty: int = 1) -> int:
    """Return the total price of the requested bakery item."""

    item = item.lower().strip()

    if qty < 1:
        raise ValueError("Quantity must be positive")

    if item not in MENU:
        raise ValueError("Item not available")

    return MENU[item] * qty

# 7. FEW-SHOT CLASSIFIER
def classify_message(message: str) -> str:

    messages = [
        {
            "role": "system",
            "content": """
            Classify the customer message into one category:
            order, question or complaint.
            Return only one word.
            """
        }
    ] + EXAMPLES + [
        {"role": "user", "content": message}
    ]

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0
        )

        return response.choices[0].message.content.strip().lower()

    except Exception as e:
        print("Classification error:", e)
        return "unknown"

# 8. JSON ORDER EXTRACTION
def extract_order(message: str):

    prompt = """
    Extract the customer order.
    Return ONLY valid JSON with:
    name (string),
    item (string),
    qty (integer),
    date (string),
    eggless (boolean).
    Do not add Markdown fences or explanations.
    Use empty strings for unknown text,
    0 for unknown quantity and false for unknown eggless status.
    """

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": message}
            ],
            temperature=0
        )

        reply = response.choices[0].message.content.strip()

        if reply.startswith("```"):
            reply = reply.replace("```json", "")
            reply = reply.replace("```", "").strip()

        order = json.loads(reply)

        return order

    except json.JSONDecodeError:
        print("Invalid JSON received")
        return None

    except Exception as e:
        print("Order extraction error:", e)
        return None

# 9. CHAT HISTORY / MEMORY
history = [
    {"role": "system", "content": SYSTEM}
]

MAX_TURNS = 8

# 10. CHAT FUNCTION WITH ERROR HANDLING
def chat(user_text: str) -> str:

    history.append({
        "role": "user",
        "content": user_text
    })

    # Keep system message and last 8 complete turns
    recent = [history[0]] + history[1:][-MAX_TURNS * 2:]

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=recent,
            temperature=0.3
        )

        reply = response.choices[0].message.content or "Please try again."

    except RateLimitError:
        reply = "We're busy. Please try again shortly."

    except AuthenticationError:
        reply = "API authentication problem. Contact the owner."

    except APIConnectionError:
        reply = "Unable to connect to the server. Try again shortly."

    except Exception as e:
        print("Error:", e)
        reply = "Something went wrong. Please try again."

    history.append({
        "role": "assistant",
        "content": reply
    })

    return reply

# 11. MAIN PROGRAM
print("=" * 45)
print(" WELCOME TO SWEET CRUMBS HOME BAKERY")
print("=" * 45)

print("\nMenu:")
for item, price in MENU.items():
    print(f"{item.title()} : Rs {price}")

print("\nPrice Function Test:")
print("Total for 6 cupcakes:", get_price("cupcake", 6))

# Classifier test
print("\nFew-Shot Classifier Test:")
print(classify_message("I need two chocolate cakes"))

# JSON extraction test
print("\nJSON Order Extraction:")
sample = "Hi, I am Ravi. I need 2 plum cakes for 24 December, eggless."

order = extract_order(sample)

if order:
    print(json.dumps(order, indent=4))

    if order.get("item", "").lower() in MENU and order.get("qty", 0) > 0:
        try:
            print("Total Price:", get_price(
                order["item"], order["qty"]
            ))
        except ValueError as e:
            print(e)

# 12. CHATBOT LOOP
print("\nChatbot is ready!")
print("Type 'exit' to stop.\n")

while True:

    user_text = input("You: ")

    if user_text.lower().strip() in ["exit", "quit", "bye"]:
        print("Bot: Thank you for visiting Sweet Crumbs!")
        break

    print("Bot:", chat(user_text))
