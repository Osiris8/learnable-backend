import os
from ollama import chat
from dotenv import load_dotenv
OLLAMA_MODELS = os.environ.get("OLLAMA_MODELS", "gpt-oss:20b").split(",")
def validate_model(model: str):
    
    if model not in OLLAMA_MODELS:
        raise ValueError(f"Model {model} is not allowed")
def ollama_service(content: str, model: str) -> str:
    validate_model(model)
    response_text = []
    
    stream = chat(
        model=model,
        messages=[{'role': 'user', 'content': content}],
        stream=True,
    )

    for chunk in stream:
        content = chunk['message']['content']
        print(content, end='', flush=True)

        response_text.append(content)

    print()
  
    return "".join(response_text)
    content_type="text/plain"

    