from app.db import get_db
def dashboard_metrics():
 with get_db() as db:
  total=db.execute("SELECT COUNT(*) c FROM leads").fetchone()["c"]; booked=db.execute("SELECT COUNT(*) c FROM leads WHERE status='booked'").fetchone()["c"]; escalated=db.execute("SELECT COUNT(*) c FROM leads WHERE status='escalated'").fetchone()["c"]; out=db.execute("SELECT COUNT(*) c FROM leads WHERE status='out_of_area'").fetchone()["c"]; human=db.execute("SELECT COUNT(*) c FROM leads WHERE status='needs_human'").fetchone()["c"]; pipeline=db.execute("SELECT COALESCE(SUM(estimated_value),0) v FROM leads WHERE status IN ('qualified','booked')").fetchone()["v"]; bookings=db.execute("SELECT COUNT(*) c FROM bookings").fetchone()["c"]
 return {"total_leads":total,"booked_leads":booked,"bookings_created":bookings,"escalated_leads":escalated,"out_of_area_leads":out,"needs_human_leads":human,"pipeline_value":pipeline,"booking_conversion_rate_percent":round(booked/total*100,1) if total else 0}
