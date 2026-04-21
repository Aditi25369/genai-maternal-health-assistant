from typing import Tuple, List

HIGH_RISK_PATTERNS = {
    "heavy_bleeding": {
        "keywords": ["heavy bleeding", "lots of blood", "bleeding won't stop", "soaking pad",
                     "ಹೆಚ್ಚು ರಕ್ತ", "रक्तस्राव", "रक्त बह"],
        "action": "Go to the nearest hospital or call 108 ambulance immediately. This is an emergency.",
        "level": "CRITICAL",
    },
    "convulsion": {
        "keywords": ["convulsion", "seizure", "fits", "shaking", "unconscious", "fainted",
                     "ಸೆಳೆತ", "ಅಪಸ್ಮಾರ", "दौरा", "बेहोश"],
        "action": "Call 108 immediately. This is a life-threatening emergency.",
        "level": "CRITICAL",
    },
    "preeclampsia": {
        "keywords": ["severe headache", "blurred vision", "can't see", "vision problem",
                     "face swelling", "hand swelling", "sudden swelling",
                     "ತಲೆನೋವು", "ದೃಷ್ಟಿ", "सिरदर्द", "धुंधला"],
        "action": "These may be signs of preeclampsia. Go to the hospital NOW. Check your blood pressure immediately.",
        "level": "HIGH",
    },
    "reduced_fetal_movement": {
        "keywords": ["baby not moving", "no movement", "reduced movement", "can't feel baby",
                     "fetal movement", "kicks stopped",
                     "ಮಗು ಅಲುಗಾಡುತ್ತಿಲ್ಲ", "बच्चा हिल नहीं रहा"],
        "action": "Reduced fetal movement after 28 weeks is a danger sign. Go to hospital immediately for fetal monitoring.",
        "level": "HIGH",
    },
    "high_fever": {
        "keywords": ["high fever", "very high temperature", "104", "105", "103",
                     "ಹೆಚ್ಚು ಜ್ವರ", "तेज बुखार", "बहुत बुखार"],
        "action": "High fever during pregnancy or in a newborn is serious. Go to the nearest PHC or hospital.",
        "level": "HIGH",
    },
    "newborn_danger": {
        "keywords": ["baby not feeding", "baby not breathing", "baby turned blue", "baby limp",
                     "baby jaundice", "yellow baby", "umbilical cord",
                     "ಮಗು ತಿನ್ನುತ್ತಿಲ್ಲ", "बच्चा नहीं पी रहा", "बच्चे को बुखार"],
        "action": "This is a newborn danger sign. Go to the nearest hospital or call 108 immediately.",
        "level": "HIGH",
    },
    "breathing_difficulty": {
        "keywords": ["can't breathe", "difficulty breathing", "shortness of breath", "chest pain",
                     "ಉಸಿರಾಟ ತೊಂದರೆ", "सांस लेने में तकलीफ"],
        "action": "Breathing difficulty is a medical emergency. Call 108 or go to hospital immediately.",
        "level": "CRITICAL",
    },
    "postpartum_depression": {
        "keywords": ["don't want to live", "want to hurt myself", "can't cope", "feel like dying",
                     "postpartum depression", "baby blues severe",
                     "जीना नहीं चाहती", "ಜೀವ ಬೇಡ"],
        "action": "Please talk to someone right now. Call iCall: 9152987821 or Vandrevala Foundation: 1860-2662-345. You are not alone.",
        "level": "CRITICAL",
    },
}

MODERATE_RISK_PATTERNS = {
    "mild_fever": {
        "keywords": ["fever", "temperature", "hot", "ज्वर", "ಜ್ವರ", "बुखार"],
        "action": "Monitor temperature. If above 38°C or persists more than 24 hours, contact your ASHA worker.",
        "level": "MODERATE",
    },
    "vomiting": {
        "keywords": ["vomiting", "throwing up", "can't keep food down", "severe nausea",
                     "ವಾಂತಿ", "उल्टी"],
        "action": "Stay hydrated with ORS. If vomiting is severe or you can't keep water down, visit your PHC.",
        "level": "MODERATE",
    },
}


def assess_risk(message: str) -> Tuple[bool, str, List[str], str]:
    message_lower = message.lower()
    detected = []
    highest_level = None
    final_action = ""

    for condition, data in HIGH_RISK_PATTERNS.items():
        for keyword in data["keywords"]:
            if keyword.lower() in message_lower:
                detected.append(condition.replace("_", " "))
                if data["level"] == "CRITICAL":
                    highest_level = "CRITICAL"
                    final_action = data["action"]
                elif highest_level != "CRITICAL":
                    highest_level = "HIGH"
                    final_action = data["action"]
                break

    if not detected:
        for condition, data in MODERATE_RISK_PATTERNS.items():
            for keyword in data["keywords"]:
                if keyword.lower() in message_lower:
                    detected.append(condition.replace("_", " "))
                    highest_level = "MODERATE"
                    final_action = data["action"]
                    break

    is_high_risk = highest_level in ["HIGH", "CRITICAL"]

    if not highest_level:
        highest_level = "LOW"
        final_action = "No immediate danger signs detected. Continue regular antenatal care."

    return is_high_risk, highest_level, detected, final_action