from fastapi import APIRouter
from models.schemas import RiskAssessRequest, RiskAssessResponse
from services.risk_service import assess_risk

router = APIRouter()


@router.post("/assess-risk", response_model=RiskAssessResponse)
async def assess_risk_endpoint(request: RiskAssessRequest):
    is_high_risk, risk_level, detected_symptoms, action = assess_risk(request.symptoms)
    return RiskAssessResponse(
        is_high_risk=is_high_risk,
        risk_level=risk_level,
        detected_symptoms=detected_symptoms,
        recommended_action=action,
    )