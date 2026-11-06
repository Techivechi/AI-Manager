from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
def test_metrics(): assert client.get("/api/metrics").status_code==200
def test_create_and_book_lead():
 r=client.post("/api/leads",json={"name":"Test Customer","phone":"+15550001234","message":"My AC is not cooling","address":"12 MG Road","service":"hvac","source":"google_ads","estimated_value":450})
 assert r.status_code==200 and r.json()["status"]=="booked"
def test_emergency_escalates():
 r=client.post("/api/leads",json={"name":"Emergency","phone":"+15550001235","message":"I smell gas in my kitchen","address":"12 MG Road","service":"plumbing"})
 assert r.status_code==200 and r.json()["status"]=="escalated"
