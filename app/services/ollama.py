import os
from ollama import chat
from dotenv import load_dotenv
OLLAMA_MODELS = os.environ.get("OLLAMA_MODELS", "gemma3:1b").split(",")
def validate_model(model: str):
    """Vérifie que le modèle est autorisé"""
    if model not in OLLAMA_MODELS:
        raise ValueError(f"Modèle non autorisé : {model}")
def ollama_service(prompt: str, model: str) -> str:
    validate_model(model)
    response_text = ""
    
    stream = chat(
        model=model,
        messages=[{'role': 'user', 'content': prompt}],
        stream=True,
    )

    for chunk in stream:
        content = chunk['message']['content']
        print(content, end='', flush=True)
        response_text += content 

    print()
    return response_text
    content_type="text/plain"