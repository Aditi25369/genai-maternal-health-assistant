from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
from models.schemas import ChatMessage, ChatResponse
from services.rag_service import get_rag_response
from services.risk_service import assess_risk
from services.firebase_service import flag_high_risk_case, get_user_profile, save_chat_message
from services.vision_service import analyze_image
import json

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatMessage):
    is_high_risk, risk_level, detected_symptoms, action = assess_risk(request.message)

    reply = get_rag_response(
        user_message=request.message,
        language=request.language.value,
        gestational_week=request.gestational_week,
        child_dob=request.child_dob,
    )

    save_chat_message(request.user_id, "user", request.message)
    save_chat_message(request.user_id, "assistant", reply)

    if is_high_risk and detected_symptoms:
        profile = get_user_profile(request.user_id)
        flag_high_risk_case(
            user_id=request.user_id,
            symptoms=", ".join(detected_symptoms),
            risk_level=risk_level,
            action=action,
            profile=profile,
        )

    return ChatResponse(
        reply=reply,
        is_high_risk=is_high_risk,
        risk_message=f"⚠️ Danger signs detected: {', '.join(detected_symptoms)}" if detected_symptoms else None,
        suggested_action=action if is_high_risk else None,
        language=request.language,
    )


@router.post("/chat/image", response_model=ChatResponse)
async def chat_with_image(
    user_id: str = Form(...),
    message: str = Form(default="Please analyze this image"),
    language: str = Form(default="english"),
    gestational_week: Optional[int] = Form(default=None),
    child_dob: Optional[str] = Form(default=None),
    image: UploadFile = File(...),
):
    image_bytes = await image.read()
    image_analysis = await analyze_image(image_bytes, message, language)

    is_high_risk, risk_level, detected_symptoms, action = assess_risk(image_analysis)

    save_chat_message(user_id, "user", f"[Image uploaded] {message}")
    save_chat_message(user_id, "assistant", image_analysis)

    if is_high_risk and detected_symptoms:
        profile = get_user_profile(user_id)
        flag_high_risk_case(
            user_id=user_id,
            symptoms=", ".join(detected_symptoms),
            risk_level=risk_level,
            action=action,
            profile=profile,
        )

    return ChatResponse(
        reply=image_analysis,
        is_high_risk=is_high_risk,
        risk_message=f"⚠️ Danger signs detected: {', '.join(detected_symptoms)}" if detected_symptoms else None,
        suggested_action=action if is_high_risk else None,
        language=language,
    )