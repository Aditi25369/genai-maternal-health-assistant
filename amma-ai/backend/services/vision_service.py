import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

VISION_SYSTEM_PROMPT = """You are Amma AI, a maternal health assistant analyzing an image uploaded by a pregnant woman or new mother.

Your job:
- Carefully analyze the image in the context of maternal or child health
- If it shows a body part (swollen feet, rash, skin condition, baby appearance), describe what you observe
- Give safe, evidence-based guidance based on what you see
- If you see anything that looks like a danger sign (severe swelling, unusual rash, baby looking unwell, yellow skin/eyes), say so clearly and recommend immediate medical attention
- NEVER give a definitive diagnosis — always recommend professional consultation
- Be warm, calm, and reassuring unless there is a genuine danger sign

Common things mothers upload:
- Swollen feet/hands (could be normal or preeclampsia sign)
- Baby skin rashes (could be normal newborn rash or infection)
- Baby jaundice (yellow skin/eyes — serious in newborns)
- Wound or stitches after delivery
- Baby's umbilical cord

Always end with: "This is an AI assessment only. Please consult your doctor or ASHA worker to confirm."
"""

LANGUAGE_INSTRUCTIONS = {
    "kannada": "Please respond in Kannada (ಕನ್ನಡ).",
    "hindi": "Please respond in Hindi (हिंदी).",
    "english": "Please respond in English.",
}


async def analyze_image(image_bytes: bytes, user_message: str = "", language: str = "english") -> str:
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")

        lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["english"])
        prompt = f"""{VISION_SYSTEM_PROMPT}

{lang_instruction}

The user says: "{user_message if user_message else 'Please analyze this image related to my health or my baby.'}"

Analyze the image carefully and provide helpful maternal health guidance."""

        image_part = {
            "mime_type": "image/jpeg",
            "data": image_bytes,
        }

        response = model.generate_content([prompt, image_part])
        return response.text

    except Exception as e:
        fallback = {
            "english": "I couldn't analyze the image right now. Please describe your symptoms in text, or contact your ASHA worker or call Karnataka 104 health helpline.",
            "kannada": "ಚಿತ್ರವನ್ನು ವಿಶ್ಲೇಷಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ನಿಮ್ಮ ರೋಗಲಕ್ಷಣಗಳನ್ನು ಪಠ್ಯದಲ್ಲಿ ವಿವರಿಸಿ ಅಥವಾ 104 ಕರೆ ಮಾಡಿ.",
            "hindi": "छवि का विश्लेषण नहीं हो सका। कृपया अपने लक्षण टेक्स्ट में बताएं या 104 हेल्पलाइन पर कॉल करें।",
        }
        return fallback.get(language, fallback["english"])