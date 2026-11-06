from fastapi import APIRouter,Request
from fastapi.responses import PlainTextResponse
from app.db import get_db,utcnow
from app.services.conversation import add_conversation
from app.services.booking import process_lead
from app.services.messaging import confirmation_message,escalation_message,send_sms
router=APIRouter(prefix="/webhooks")
@router.post("/sms",response_class=PlainTextResponse)
async def inbound_sms(request:Request):
 form=await request.form(); from_number=form.get("From",""); body=form.get("Body","")
 with get_db() as db:
  cur=db.execute("INSERT INTO leads (name,phone,message,source,created_at,updated_at) VALUES (?,?,?,?,?,?)",("SMS Lead",from_number,body,"sms",utcnow(),utcnow())); lid=cur.lastrowid
 add_conversation(lid,"sms","inbound",body); process_lead(lid)
 with get_db() as db: lead=dict(db.execute("SELECT * FROM leads WHERE id=?",(lid,)).fetchone()); booking=db.execute("SELECT * FROM bookings WHERE lead_id=?",(lid,)).fetchone()
 message=confirmation_message(lead["name"],lead["service"],booking["slot"],booking["external_id"]) if booking else escalation_message(lead["name"])
 send_sms(from_number,message); add_conversation(lid,"sms","outbound",message)
 return PlainTextResponse(f"<?xml version='1.0' encoding='UTF-8'?><Response><Message>{message}</Message></Response>",media_type="application/xml")
@router.post("/voice",response_class=PlainTextResponse)
async def inbound_voice(request:Request):
 form=await request.form(); from_number=form.get("From","")
 with get_db() as db:
  cur=db.execute("INSERT INTO leads (name,phone,message,source,status,created_at,updated_at) VALUES (?,?,?,?,?,?,?)",("Voice Lead",from_number,"Inbound call received; AI intake pending.","voice","needs_human",utcnow(),utcnow())); lid=cur.lastrowid
 add_conversation(lid,"voice","inbound","Inbound call received")
 message="Thanks for calling. Please describe your issue, and we will connect you with the right technician."
 return PlainTextResponse(f"<?xml version='1.0' encoding='UTF-8'?><Response><Say>{message}</Say></Response>",media_type="application/xml")
