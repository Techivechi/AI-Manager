import json, sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from app.config import settings
DB_PATH=settings.database_url.replace("sqlite:///","")
Path(DB_PATH).parent.mkdir(parents=True,exist_ok=True)
SCHEMA="""
CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY CHECK(id=1),business_name TEXT,business_phone TEXT,emergency_phone TEXT,service_areas TEXT,business_hours TEXT,auto_booking_enabled INTEGER DEFAULT 1,updated_at TEXT);
CREATE TABLE IF NOT EXISTS leads (id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,phone TEXT,message TEXT,address TEXT DEFAULT '',service TEXT DEFAULT 'hvac',source TEXT DEFAULT 'direct',urgency TEXT DEFAULT 'unknown',status TEXT DEFAULT 'new',service_area_ok INTEGER DEFAULT 0,escalation_reason TEXT,booking_id INTEGER,estimated_value REAL DEFAULT 0,created_at TEXT,updated_at TEXT);
CREATE TABLE IF NOT EXISTS conversations (id INTEGER PRIMARY KEY AUTOINCREMENT,lead_id INTEGER,channel TEXT,direction TEXT,content TEXT,metadata TEXT DEFAULT '{}',created_at TEXT);
CREATE TABLE IF NOT EXISTS bookings (id INTEGER PRIMARY KEY AUTOINCREMENT,lead_id INTEGER,external_id TEXT,slot TEXT,status TEXT,service TEXT,address TEXT,created_at TEXT);
CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT,lead_id INTEGER,event_type TEXT,payload TEXT DEFAULT '{}',created_at TEXT);
"""
def utcnow(): return datetime.now(timezone.utc).isoformat()
def connect():
 c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; c.execute("PRAGMA foreign_keys=ON"); return c
@contextmanager
def get_db():
 c=connect()
 try: yield c; c.commit()
 finally: c.close()
def init_db():
 with get_db() as db:
  db.executescript(SCHEMA)
  if not db.execute("SELECT 1 FROM settings WHERE id=1").fetchone():
   db.execute("INSERT INTO settings VALUES (1,?,?,?,?,?,?,?)",("Demo Home Services","+15550000000","+15550000001",json.dumps(["MG Road","Indiranagar","Koramangala","Whitefield"]),"mon-fri:09:00-18:00;sat:10:00-16:00",1,utcnow()))
def get_settings():
 with get_db() as db: r=db.execute("SELECT * FROM settings WHERE id=1").fetchone()
 return dict(r) if r else {}
def save_settings(d):
 with get_db() as db: db.execute("UPDATE settings SET business_name=?,business_phone=?,emergency_phone=?,service_areas=?,business_hours=?,auto_booking_enabled=?,updated_at=? WHERE id=1",(d.get("business_name"),d.get("business_phone"),d.get("emergency_phone"),json.dumps(d.get("service_areas",[])),d.get("business_hours"),1 if d.get("auto_booking_enabled",True) else 0,utcnow()))
def log_event(lead_id,event_type,payload=None):
 with get_db() as db: db.execute("INSERT INTO events (lead_id,event_type,payload,created_at) VALUES (?,?,?,?)",(lead_id,event_type,json.dumps(payload or {}),utcnow()))
