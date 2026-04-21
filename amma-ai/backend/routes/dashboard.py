from fastapi import APIRouter
from models.schemas import DashboardResponse, FlaggedCase
from services.firebase_service import get_flagged_cases, get_dashboard_stats

router = APIRouter()


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard():
    raw_cases = get_flagged_cases()
    cases = []
    for c in raw_cases:
        cases.append(FlaggedCase(
            user_id=c.get("user_id", ""),
            name=c.get("name", "Unknown"),
            phone=c.get("phone", ""),
            location=c.get("location", ""),
            symptoms=c.get("symptoms", ""),
            risk_level=c.get("risk_level", ""),
            timestamp=c.get("timestamp", ""),
            recommended_action=c.get("recommended_action", ""),
        ))
    stats = get_dashboard_stats()
    return DashboardResponse(
        flagged_cases=cases,
        total_users=stats.get("total_users", 0),
        high_risk_count=stats.get("high_risk_count", 0),
    )