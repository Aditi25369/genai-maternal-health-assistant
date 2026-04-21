from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class Language(str, Enum):
    english = "english"
    kannada = "kannada"
    hindi = "hindi"

class UserProfile(BaseModel):
    user_id: str
    name: str
    language: Language = Language.english
    gestational_week: Optional[int] = None
    child_dob: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None

class ChatMessage(BaseModel):
    user_id: str
    message: str
    language: Language = Language.english
    gestational_week: Optional[int] = None
    child_dob: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    is_high_risk: bool = False
    risk_message: Optional[str] = None
    suggested_action: Optional[str] = None
    language: Language = Language.english

class RiskAssessRequest(BaseModel):
    user_id: str
    symptoms: str
    gestational_week: Optional[int] = None

class RiskAssessResponse(BaseModel):
    is_high_risk: bool
    risk_level: str
    detected_symptoms: List[str]
    recommended_action: str

class ReminderRequest(BaseModel):
    user_id: str
    gestational_week: Optional[int] = None
    child_dob: Optional[str] = None

class ReminderCreateRequest(BaseModel):
    user_id: str
    title: str
    description: str
    scheduled_time: str
    type: str = "custom"

class Reminder(BaseModel):
    id: Optional[str] = None
    user_id: str
    title: str
    description: str
    scheduled_time: str
    type: str = "custom"
    is_completed: bool = False
    created_at: Optional[str] = None

class ReminderResponse(BaseModel):
    reminders: List[Reminder]

class FlaggedCase(BaseModel):
    user_id: str
    name: str
    phone: Optional[str] = None
    location: Optional[str] = None
    symptoms: str
    risk_level: str
    timestamp: str
    recommended_action: str

class DashboardResponse(BaseModel):
    flagged_cases: List[FlaggedCase]
    total_users: int
    high_risk_count: int