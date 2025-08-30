from app.services.ollama import ollama_service
def tutor_agent(prompt: str, model: str) -> str:
    return ollama_service(f"""
    You are a Tutor Agent.
    If the prompt includes (course, lesson, learning), create a structured course (intro, outline, explanations, exercises, quiz, final project).
    Otherwise answer simply as a tutor.

    Prompt: "{prompt}"
    """, model=model)


def sante_agent(prompt: str, model: str) -> str:
    return ollama_service(f"""
    You are a Health Agent.
    Provide general wellness advice, explain concepts clearly, but DO NOT give medical diagnoses.

    Prompt: "{prompt}"
    """, model=model)


def agriculture_agent(prompt: str, model: str) -> str:
    return ollama_service(f"""
    You are an Agriculture Agent.
    Provide tips about crops, farming techniques, soil, irrigation, and sustainable agriculture.

    Prompt: "{prompt}"
    """, model=model)

agents = {
    "tutor": tutor_agent,
    "sante": sante_agent,
    "agriculture": agriculture_agent
}


