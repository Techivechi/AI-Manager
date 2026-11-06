from app.config import settings
def confirmation_message(name,service,slot,booking_id): return f"Hi {name}, your {service.upper()} appointment is confirmed for {slot}. Reference: {booking_id}. Reply STOP to opt out."
def escalation_message(name): return f"Hi {name}, we received your request. A team member will contact you shortly regarding your urgent issue."
def out_of_area_message(name): return f"Hi {name}, unfortunately we do not currently serve your location."
def send_sms(to,body):
 if not settings.twilio_account_sid or not settings.twilio_auth_token: return {"sent":False,"reason":"Twilio credentials not configured","body":body}
 return {"sent":False,"reason":"Twilio send not enabled in this sandbox","body":body}
