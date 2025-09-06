import os
from flask import Flask, Blueprint,Response, request, stream_with_context
from ollama import chat
from dotenv import load_dotenv

load_dotenv()

test_bp = Blueprint("test", __name__)

# Liste des modèles autorisés depuis la variable d'environnement
OLLAMA_MODELS = os.environ.get("OLLAMA_MODELS", "gemma3:1b").split(",")

def validate_model(model: str):
    if model not in OLLAMA_MODELS:
        raise ValueError(f"Model {model} is not allowed")

@test_bp.route("/test", methods=["POST"])
def stream_chat():
    data = request.get_json()
    content = data.get("content")
    model = data.get("model", OLLAMA_MODELS[0])  # modèle par défaut

    validate_model(model)

    def generate():
        stream = chat(
            model=model,
            messages=[{"role": "user", "content": content}],
            stream=True,
        )
        for chunk in stream:
            piece = chunk["message"]["content"]
            yield piece  # envoie direct au frontend

    return Response(stream_with_context(generate()), mimetype="text/plain")


