import json
from app.db import get_db,get_settings,log_event,utcnow
EMERGENCY=["gas leak","gas smell","fire","smoke","spark","electrical fire","flood","burst pipe","carbon monoxide","burning smell","shock"]
URGENT=["no cooling","not cooling","no ac","no air","not working","broken","leaking","leak","no hot water","no heat","overflow","clogged"]
def add_conversation(lead_id,channel,direction,content,metadata=None):
 with get_db() as db: db.execute("INSERT INTO conversations (lead_id,channel,direction,content,metadata,created_at) VALUES (?,?,?,?,?,?)",(lead_id,channel,direction,content,json.dumps(metadata or {}),utcnow()))
def classify_urgency(message):
 t=(message or "").lower()
 if any(k in t for k in EMERGENCY): return "emergency"
 if any(k in t for k in URGENT): return "urgent"
 return "routine" if t.strip() else "unknown"
def in_service_area(address,areas):
 if not areas: return True
 a=(address or "").lower(); return any(x.lower() in a for x in areas)
def qualify_lead(lead_id):
 with get_db() as db:
  lead=db.execute("SELECT * FROM leads WHERE id=?",(lead_id,)).fetchone()
  if not lead: raise ValueError("Lead not found")
  areas=json.loads(get_settings().get("service_areas","[]")); urgency=classify_urgency(lead["message"]); area_ok=in_service_area(lead["address"],areas)
  if urgency=="emergency": status,reason="escalated","Potential safety emergency; immediate human escalation required."
  elif not area_ok: status,reason="out_of_area","Customer address is outside the configured service area."
  elif urgency=="unknown": status,reason="needs_human","The customer issue could not be determined."
  else: status,reason="qualified",None
  db.execute("UPDATE leads SET urgency=?,status=?,service_area_ok=?,escalation_reason=?,updated_at=? WHERE id=?",(urgency,status,int(area_ok),reason,utcnow(),lead_id))
 log_event(lead_id,"lead_qualified",{"urgency":urgency,"service_area_ok":area_ok,"status":status})
 return {"urgency":urgency,"service_area_ok":area_ok,"status":status,"escalation_reason":reason}
