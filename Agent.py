import os
import ollama

""" client = ollama.Client(
    host=os.environ.get("OLLAMA_HOST", "http://host.docker.internal:11434")
)"""

client = ollama.Client(
    host=os.environ.get("OLLAMA_HOST", "http://localhost:11434/")
)


def add(a: float, b: float) -> float:
    return a + b


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add",
            "description": "Add two numbers",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "The first number"},
                    "b": {"type": "number", "description": "The second number"},
                },
                "required": ["a", "b"],
            },
        },
    }
]

messages = []

while True:
    try:
        user = input("you> ")
    except (EOFError, KeyboardInterrupt):
        print("\nbye")
        break

    messages.append({"role": "user", "content": user})

    for _ in range(5):  # at most 5 model calls per question
        resp = client.chat(model="qwen2.5:7b", messages=messages, tools=TOOLS)
        msg = resp.message
        messages.append(msg)

        if not msg.tool_calls:
            print("agent>", msg.content)
            break

        for call in msg.tool_calls:
            try:
                result = add(**call.function.arguments)
            except Exception as e:
                result = f"Error: {e}"
            messages.append({
                "role": "tool",
                "content": str(result),
                "tool_name": call.function.name,
            })