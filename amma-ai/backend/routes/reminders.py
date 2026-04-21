from fastapi import APIRouter
from models.schemas import ReminderRequest, ReminderResponse, Reminder
from datetime import datetime, date

router = APIRouter()


def get_pregnancy_reminders(week: int, user_id: str) -> list:
    reminders = []
    if week <= 12:
        reminders.append(Reminder(user_id=user_id, title="IFA Tablets", description="Start Iron Folic Acid tablet daily", scheduled_time="daily", priority="HIGH"))
        reminders.append(Reminder(user_id=user_id, title="First ANC Visit", description="First antenatal checkup — blood test, BP, weight", scheduled_time="this week", priority="HIGH"))
    if 12 <= week <= 20:
        reminders.append(Reminder(user_id=user_id, title="Anomaly Scan", description="Ultrasound scan to check baby's development", scheduled_time="this week", priority="HIGH"))
        reminders.append(Reminder(user_id=user_id, title="Second ANC Visit", description="Blood pressure, urine test, fundal height check", scheduled_time="this month", priority="MEDIUM"))
    if 24 <= week <= 28:
        reminders.append(Reminder(user_id=user_id, title="Glucose Test", description="Gestational diabetes screening test", scheduled_time="this week", priority="MEDIUM"))
        reminders.append(Reminder(user_id=user_id, title="TT Vaccination", description="Tetanus Toxoid vaccine if not done", scheduled_time="this month", priority="HIGH"))
    if 28 <= week <= 32:
        reminders.append(Reminder(user_id=user_id, title="Third ANC Visit", description="Check baby position, fetal heart rate", scheduled_time="this week", priority="HIGH"))
        reminders.append(Reminder(user_id=user_id, title="Kick Count", description="Count baby kicks daily — 10 kicks in 2 hours is normal", scheduled_time="daily", priority="MEDIUM"))
    if week >= 36:
        reminders.append(Reminder(user_id=user_id, title="Fourth ANC Visit", description="Check baby position, birth preparedness plan", scheduled_time="this week", priority="HIGH"))
        reminders.append(Reminder(user_id=user_id, title="Hospital Bag", description="Pack hospital bag — documents, clothes, baby items", scheduled_time="this week", priority="MEDIUM"))
        reminders.append(Reminder(user_id=user_id, title="JSY Registration", description="Register for Janani Suraksha Yojana cash benefit", scheduled_time="this week", priority="MEDIUM"))
    return reminders


def get_newborn_reminders(child_dob_str: str, user_id: str) -> list:
    reminders = []
    try:
        dob = datetime.strptime(child_dob_str, "%Y-%m-%d").date()
        today = date.today()
        age_days = (today - dob).days

        if age_days == 0:
            reminders.append(Reminder(user_id=user_id, title="Birth Vaccines", description="BCG, OPV 0, Hepatitis B — give today at hospital", scheduled_time=child_dob_str, priority="HIGH"))
        if 40 <= age_days <= 50:
            reminders.append(Reminder(user_id=user_id, title="6-week Vaccines", description="OPV 1, Pentavalent 1, Rotavirus 1, PCV 1 — due now", scheduled_time="this week", priority="HIGH"))
        if 65 <= age_days <= 77:
            reminders.append(Reminder(user_id=user_id, title="10-week Vaccines", description="OPV 2, Pentavalent 2, Rotavirus 2, PCV 2 — due now", scheduled_time="this week", priority="HIGH"))
        if 90 <= age_days <= 105:
            reminders.append(Reminder(user_id=user_id, title="14-week Vaccines", description="OPV 3, Pentavalent 3, PCV 3, IPV — due now", scheduled_time="this week", priority="HIGH"))
        if age_days < 180:
            reminders.append(Reminder(user_id=user_id, title="Exclusive Breastfeeding", description="Continue exclusive breastfeeding for 6 months — no water, no food", scheduled_time="daily", priority="HIGH"))
        if 270 <= age_days <= 290:
            reminders.append(Reminder(user_id=user_id, title="9-month Vaccines", description="MR vaccine and Vitamin A dose — due now", scheduled_time="this week", priority="HIGH"))
        if age_days < 42:
            reminders.append(Reminder(user_id=user_id, title="Postpartum Checkup", description="Mother's 6-week postnatal visit — important for recovery", scheduled_time="this week", priority="HIGH"))
    except Exception:
        reminders.append(Reminder(user_id=user_id, title="Newborn Care", description="Ensure all birth vaccines are given. Visit PHC for vaccination schedule.", scheduled_time="this week", priority="HIGH"))
    return reminders


@router.post("/reminders", response_model=ReminderResponse)
async def get_reminders(request: ReminderRequest):
    reminders = []
    if request.gestational_week:
        reminders = get_pregnancy_reminders(request.gestational_week, request.user_id)
    elif request.child_dob:
        reminders = get_newborn_reminders(request.child_dob, request.user_id)
    else:
        reminders = [Reminder(user_id=request.user_id, title="Set Up Profile", description="Add your gestational week or baby's date of birth to get personalized reminders", scheduled_time="today", priority="MEDIUM")]
    return ReminderResponse(reminders=reminders)