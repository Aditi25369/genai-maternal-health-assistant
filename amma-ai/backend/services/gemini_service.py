import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
gemini_available = False

if api_key and api_key != "your_gemini_api_key_here":
    try:
        genai.configure(api_key=api_key)
        gemini_available = True
        print("Gemini API configured successfully")
    except Exception as e:
        print(f"Gemini API config failed: {e}")
else:
    print("No Gemini API key found. Running in knowledge-base-only mode.")

SYSTEM_PROMPT = """You are Amma AI, a warm and trusted maternal health companion for pregnant women
and new mothers in India, especially in Karnataka.

Your role:
- Provide accurate, safe maternal and child health guidance based on WHO and NHM India guidelines
- Respond in the SAME language the user writes in (Kannada, Hindi, or English)
- Be warm, empathetic, and non-judgmental like a knowledgeable friend
- Always ground answers in the medical context provided to you

Safety rules:
- NEVER diagnose diseases or prescribe medicines
- For any danger signs, ALWAYS say: contact your ASHA worker or go to the nearest government hospital immediately
- Keep responses concise and easy to understand for non-medical users
- End responses about symptoms with: Karnataka 104 health helpline
"""


def build_prompt(user_message: str, context_chunks: list, gestational_week: int = None, child_dob: str = None) -> str:
    context_text = ""
    if context_chunks:
        context_text = "\n\nRelevant medical context (from WHO/NHM guidelines):\n"
        for chunk in context_chunks:
            context_text += f"- {chunk['topic'].upper()}: {chunk['content']}\n"

    user_context = ""
    if gestational_week:
        user_context = f"\nUser context: Currently {gestational_week} weeks pregnant."
    elif child_dob:
        user_context = f"\nUser context: Has a newborn (date of birth: {child_dob})."

    return f"{context_text}{user_context}\n\nUser question: {user_message}"


def knowledge_base_fallback(user_message: str, context_chunks: list, gestational_week: int = None) -> str:
    if not context_chunks:
        return (
            "For any health concerns during pregnancy or for your newborn, "
            "please contact your ASHA worker or call the Karnataka 104 health helpline. "
            "For emergencies, call 108."
        )

    response_parts = []
    for chunk in context_chunks[:2]:
        topic = chunk["topic"].title()
        content = chunk["content"]
        response_parts.append(f"**{topic}**\n{content}")

    response = "\n\n".join(response_parts)

    if gestational_week:
        response += f"\n\n_(Based on your current week {gestational_week} of pregnancy)_"

    response += "\n\n📞 For personalised advice, contact your ASHA worker or call **Karnataka 104 health helpline**."
    return response


def get_gemini_response(prompt: str, language: str = "english", user_message: str = "", context_chunks: list = None, gestational_week: int = None) -> str:
    if gemini_available:
        try:
            model = genai.GenerativeModel(
                model_name="gemini-2.0-flash",
                system_instruction=SYSTEM_PROMPT
            )
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            error_str = str(e).lower()
            print(f"Gemini API error: {e}")
            if "quota" in error_str or "429" in error_str or "limit" in error_str:
                print("Quota exceeded — using knowledge base fallback")
                return knowledge_base_fallback(user_message, context_chunks or [], gestational_week)
            fallback = {
                "english": "I'm having trouble connecting right now. Please call the Karnataka 104 health helpline. For emergencies, call 108.",
                "kannada": "ಸಂಪರ್ಕಿಸಲು ತೊಂದರೆ ಆಗುತ್ತಿದೆ. ದಯವಿಟ್ಟು 104 ಕರೆ ಮಾಡಿ. ತುರ್ತು ಸಂದರ್ಭದಲ್ಲಿ 108 ಕರೆ ಮಾಡಿ.",
                "hindi": "अभी कनेक्ट करने में समस्या है। कृपया 104 हेल्पलाइन पर कॉल करें। आपातकाल में 108 कॉल करें।",
            }
            return fallback.get(language, fallback["english"])
    else:
        return knowledge_base_fallback(user_message, context_chunks or [], gestational_week)