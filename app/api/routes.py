from fastapi import APIRouter,HTTPException,Query
from app.db import get_db,get_settings,save_settings,log_event,utcnow
from app.schemas import LeadCreate,SettingsUpdate,LeadUpdate
from app.services.conversation import add_conversation
from app.services.booking import process_lead
from app.services.messaging import confirmation_message,escalation_message,out_of_area_message,send_sms
from app.services.analytics import dashboard_metrics
router=APIRouter(prefix="/api")
@router.get("/settings")
def read_settings():
 s=get_settings(); s["service_areas"]=json.loads(s.get("service_areas","[]")); return s
@router.put("/settings")
def update_settings(p:SettingsUpdate): save_settings(p.model_dump()); return read_settings()
@router.post("/leads")
def create_lead(p:LeadCreate):
 with get_db() as db:
  cur=db.execute("INSERT INTO leads (name,phone,message,address,service,source,estimated_value,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?)",(p.name,p.phone,p.message,p.address,p.service,p.source,p.estimated_value,utcnow(),utcnow())); lid=cur.lastrowid
 add_conversation(lid,p.source,"inbound",p.message); log_event(lid,"lead_created",{"source":p.source}); result=process_lead(lid)
 with get_db() as db: lead=dict(db.execute("SELECT * FROM leads WHERE id=?",(lid,)).fetchone()); booking=db.execute("SELECT * FROM bookings WHERE lead_id=?",(lid,)).fetchone()
 if booking: message=confirmation_message(lead["name"],lead["service"],booking["slot"],booking["external_id"])
 elif lead["status"]=="out_of_area": message=out_of_area_message(lead["name"])
 else: message=escalation_message(lead["name"])
 send_sms(lead["phone"],message); add_conversation(lid,"sms","outbound",message)
 return {"lead_id":lid,"status":lead["status"],"urgency":lead["urgency"],"booking":dict(booking) if booking else None,"message":message,"processing":result}
@router.get("/leads")
def list_leads(status:str|None=Query(None),limit:int=50):
 q="SELECT * FROM leads"; params=[]
 if status: q+=" WHERE status=?"; params.append(status)
 q+=" ORDER BY id DESC LIMIT ?"; params.append(limit)
 with get_db() as db: rows=[dict(r) for r in db.execute(q,params).fetchall()]
 return {"leads":rows}
@router.get("/leads/{lead_id}")
def get_lead(lead_id:int):
 with get_db() as db:
  lead=db.execute("SELECT * FROM leads WHERE id=?",(lead_id,)).fetchone()
  if not lead: raise HTTPException(404,"Lead not found")
  conv=[dict(r) for r in db.execute("SELECT * FROM conversations WHERE lead_id=? ORDER BY id",(lead_id,)).fetchall()]
  bookings=[dict(r) for r in db.execute("SELECT * FROM bookings WHERE lead_id=? ORDER BY id",(lead_id,)).fetchall()]
 return {"lead":dict(lead),"conversations":conv,"bookings":bookings}
@router.patch("/leads/{lead_id}")
def update_lead(lead_id:int,p:LeadUpdate):
 fields=[]; values=[]
 for k,v in p.model_dump(exclude_unset=True).items(): fields.append(f"{k}=?"); values.append(v)
 if not fields: raise HTTPException(400,"No fields to update")
 fields.append("updated_at=?"); values.extend([utcnow(),lead_id])
 with get_db() as db:
  cur=db.execute(f"UPDATE leads SET {', '.join(fields)} WHERE id=?",values)
  if cur.rowcount==0: raise HTTPException(404,"Lead not found")
 log_event(lead_id,"lead_updated",p.model_dump(exclude_unset=True)); return {"updated":True}
@router.get("/metrics")
def metrics(): return dashboard_metrics()
