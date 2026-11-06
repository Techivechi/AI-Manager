from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.api.routes import router as api_router
from app.api.webhooks import router as webhook_router
from app.db import init_db,get_db
from app.dashboard import DASHBOARD_HTML
from app.services.analytics import dashboard_metrics
app=FastAPI(title="AI Branch Manager",version="1.0.0")
init_db(); app.include_router(api_router); app.include_router(webhook_router)
@app.get("/",response_class=HTMLResponse)
def root(): return HTMLResponse("<h1>AI Branch Manager</h1><p><a href=/dashboard>Dashboard</a> | <a href=/docs>API docs</a></p>")
@app.get("/dashboard",response_class=HTMLResponse)
def dashboard():
 m=dashboard_metrics()
 with get_db() as db: rows=db.execute("SELECT * FROM leads ORDER BY id DESC LIMIT 25").fetchall()
 rows_html="".join(f"<tr><td>{r['name']}</td><td>{r['phone']}</td><td>{r['service']}</td><td>{r['urgency']}</td><td><span class='badge {r['status']}'><>{r['status']}</span></td><td>{r['estimated_value']}</td></tr>" for r in rows)
 html=DASHBOARD_HTML.replace("__TOTAL__",str(m["total_leads"])).replace("__BOOKED__",str(m["booked_leads"])).replace("__CONVERSION__",str(m["booking_conversion_rate_percent"])).replace("__PIPELINE__",f"{m['pipeline_value']:,.0f}").replace("__ESCALATED__",str(m["escalated_leads"])).replace("__NEEDS_HUMAN__",str(m["needs_human_leads"])).replace("__ROWS__",rows_html)
 return HTMLResponse(html)
