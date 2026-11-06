import os,uuid
from abc import ABC,abstractmethod
from datetime import datetime,timedelta
from app.db import get_db,get_settings,log_event,utcnow
from app.services.conversation import qualify_lead
class BookingService(ABC):
 @abstractmethod
def check_availability(self,lead):...
 @abstractmethod
def create_booking(self,lead,slot):...
class MockBookingService(BookingService):
 def check_availability(self,lead): return {"available":True,"slot":(datetime.now()+timedelta(days=1 if lead["urgency"]=="urgent" else 3)).strftime("%Y-%m-%d %H:%M")}
 def create_booking(self,lead,slot): return {"external_id":f"MOCK-{uuid.uuid4().hex[:10].upper()}","slot":slot,"status":"booked"}
class JobberBookingService(BookingService):
 def check_availability(self,lead): raise NotImplementedError("Connect Jobber credentials and implement availability lookup.")
 def create_booking(self,lead,slot): raise NotImplementedError("Connect Jobber credentials and implement booking mutation.")
def get_booking_service():
 return JobberBookingService() if os.getenv("BOOKING_PROVIDER")=="jobber" else MockBookingService()
def process_lead(lead_id):
 qualify_lead(lead_id)
 with get_db() as db: lead=dict(db.execute("SELECT * FROM leads WHERE id=?",(lead_id,)).fetchone()); settings=get_settings()
 if lead["status"]!="qualified": return {"lead_id":lead_id,"status":lead["status"],"booked":False,"reason":lead["escalation_reason"]}
 if not settings.get("auto_booking_enabled"): return {"lead_id":lead_id,"status":"qualified","booked":False,"reason":"Auto-booking is disabled."}
 service=get_booking_service(); availability=service.check_availability(lead)
 if not availability.get("available"): return {"lead_id":lead_id,"status":"no_availability","booked":False}
 booking=service.create_booking(lead,availability["slot"])
 with get_db() as db:
  cur=db.execute("INSERT INTO bookings (lead_id,external_id,slot,status,service,address,created_at) VALUES (?,?,?,?,?,?,?)",(lead_id,booking["external_id"],booking["slot"],booking["status"],lead["service"],lead["address"],utcnow())); bid=cur.lastrowid
  db.execute("UPDATE leads SET status='booked',booking_id=?,updated_at=? WHERE id=?",(bid,utcnow(),lead_id))
 log_event(lead_id,"booking_created",booking)
 return {"lead_id":lead_id,"status":"booked","booked":True,"booking":booking}
