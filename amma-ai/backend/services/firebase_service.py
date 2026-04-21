import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

db = None
firebase_available = False

try:
    import firebase_admin
    from firebase_admin import credentials, firestore

    cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase_credentials.json")
    if os.path.exists(cred_path):
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        firebase_available = True
        print("Firebase connected successfully")
    else:
        print("Firebase credentials not found. Running in local mode.")
except Exception as e:
    print(f"Firebase not available: {e}. Running in local mode.")


# ── DEMO DATA for hackathon presentation ──
DEMO_FLAGGED_CASES = [
    {
        "user_id": "demo_user_1",
        "name": "Priya Sharma",
        "phone": "+91 98765 43210",
        "location": "Koramangala, Bengaluru",
        "symptoms": "severe headache, sudden swelling",
        "risk_level": "CRITICAL",
        "recommended_action": "These may be signs of preeclampsia. Go to the hospital NOW. Check blood pressure immediately.",
        "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat(),
        "resolved": False,
    },
    {
        "user_id": "demo_user_2",
        "name": "Kavitha R",
        "phone": "+91 87654 32109",
        "location": "Jayanagar, Bengaluru",
        "symptoms": "reduced fetal movement",
        "risk_level": "HIGH",
        "recommended_action": "Reduced fetal movement after 28 weeks is a danger sign. Go to hospital immediately for fetal monitoring.",
        "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
        "resolved": False,
    },
    {
        "user_id": "demo_user_3",
        "name": "Fatima Begum",
        "phone": "+91 76543 21098",
        "location": "Shivajinagar, Bengaluru",
        "symptoms": "newborn not feeding, high fever in baby",
        "risk_level": "HIGH",
        "recommended_action": "Newborn danger sign. Go to nearest hospital or call 108 immediately.",
        "timestamp": (datetime.now() - timedelta(hours=3)).isoformat(),
        "resolved": False,
    },
    {
        "user_id": "demo_user_4",
        "name": "Suma Patil",
        "phone": "+91 65432 10987",
        "location": "Yelahanka, Bengaluru",
        "symptoms": "heavy bleeding after delivery",
        "risk_level": "CRITICAL",
        "recommended_action": "Go to the nearest hospital or call 108 ambulance immediately. This is an emergency.",
        "timestamp": (datetime.now() - timedelta(hours=5)).isoformat(),
        "resolved": False,
    },
]

DEMO_USERS = {
    "demo_user_1": {"name": "Priya Sharma", "language": "english", "gestational_week": 32, "location": "Koramangala"},
    "demo_user_2": {"name": "Kavitha R", "language": "kannada", "gestational_week": 30, "location": "Jayanagar"},
    "demo_user_3": {"name": "Fatima Begum", "language": "hindi", "child_dob": "2026-03-25", "location": "Shivajinagar"},
    "demo_user_4": {"name": "Suma Patil", "language": "kannada", "child_dob": "2026-04-10", "location": "Yelahanka"},
}

LOCAL_STORE = {
    "users": dict(DEMO_USERS),
    "flagged_cases": list(DEMO_FLAGGED_CASES),
    "chat_history": {},
}


def save_user_profile(user_id: str, profile: dict):
    try:
        if firebase_available:
            db.collection("users").document(user_id).set(profile)
        else:
            LOCAL_STORE["users"][user_id] = profile
        return True
    except Exception as e:
        print(f"Error saving user: {e}")
        return False


def get_user_profile(user_id: str) -> dict:
    try:
        if firebase_available:
            doc = db.collection("users").document(user_id).get()
            return doc.to_dict() if doc.exists else None
        else:
            return LOCAL_STORE["users"].get(user_id)
    except Exception as e:
        print(f"Error getting user: {e}")
        return None


def flag_high_risk_case(user_id: str, symptoms: str, risk_level: str, action: str, profile: dict = None):
    try:
        case = {
            "user_id": user_id,
            "name": profile.get("name", "Unknown") if profile else "Unknown",
            "phone": profile.get("phone", "") if profile else "",
            "location": profile.get("location", "") if profile else "",
            "symptoms": symptoms,
            "risk_level": risk_level,
            "recommended_action": action,
            "timestamp": datetime.now().isoformat(),
            "resolved": False,
        }
        if firebase_available:
            db.collection("flagged_cases").add(case)
        else:
            LOCAL_STORE["flagged_cases"].insert(0, case)
        return True
    except Exception as e:
        print(f"Error flagging case: {e}")
        return False


def get_flagged_cases() -> list:
    try:
        if firebase_available:
            cases = db.collection("flagged_cases").where(
                "resolved", "==", False
            ).limit(50).get()
            return [c.to_dict() for c in cases]
        else:
            return sorted(
                [c for c in LOCAL_STORE["flagged_cases"] if not c.get("resolved", False)],
                key=lambda x: x["timestamp"],
                reverse=True,
            )
    except Exception as e:
        print(f"Error getting flagged cases: {e}")
        return []


def get_dashboard_stats() -> dict:
    try:
        flagged = get_flagged_cases()
        high_risk = len([c for c in flagged if c.get("risk_level") in ["HIGH", "CRITICAL"]])
        return {
            "total_users": len(LOCAL_STORE["users"]),
            "high_risk_count": high_risk,
        }
    except Exception as e:
        return {"total_users": 0, "high_risk_count": 0}


def save_chat_message(user_id: str, role: str, message: str):
    try:
        entry = {
            "role": role,
            "message": message,
            "timestamp": datetime.now().isoformat(),
        }
        if firebase_available:
            db.collection("chat_history").document(user_id).collection("messages").add(entry)
        else:
            if user_id not in LOCAL_STORE["chat_history"]:
                LOCAL_STORE["chat_history"][user_id] = []
            LOCAL_STORE["chat_history"][user_id].append(entry)
    except Exception as e:
        print(f"Error saving chat: {e}")