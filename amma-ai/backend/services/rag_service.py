from data.knowledge_base import search_knowledge
from services.gemini_service import build_prompt, get_gemini_response


def get_rag_response(
    user_message: str,
    language: str = "english",
    gestational_week: int = None,
    child_dob: str = None,
) -> str:
    relevant_chunks = search_knowledge(user_message, top_k=3)
    prompt = build_prompt(
        user_message=user_message,
        context_chunks=relevant_chunks,
        gestational_week=gestational_week,
        child_dob=child_dob,
    )
    response = get_gemini_response(prompt, language, user_message, relevant_chunks, gestational_week)
    return response