from app.services.ollama import ollama_service
def edu_mentor_agent(prompt: str, model: str) -> str:
    return ollama_service(f"""
    You are a Tutor Agent.
    If the prompt includes (course, lesson, learning), create a structured course (intro, outline, explanations, exercises, quiz, final project).
    Otherwise answer simply as a tutor.

    Prompt: "{prompt}"
    """, model=model)


def medi_assist_agent(prompt: str, model: str) -> str:
    return ollama_service(f"""
    You are a Health Agent.
    Provide general wellness advice, explain concepts clearly, but DO NOT give medical diagnoses.

    Prompt: "{prompt}"
    """, model=model)


def green_helper_agent(prompt: str, model: str) -> str:
    return ollama_service(f"""
    You are an Agriculture Agent.
    Provide tips about crops, farming techniques, soil, irrigation, and sustainable agriculture.

    Prompt: "{prompt}"
    """, model=model)

agents = {
    "tutor": edu_mentor_agent,
    "health": medi_assist_agent,
    "agriculture": green_helper_agent
}


