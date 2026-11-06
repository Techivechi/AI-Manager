# AI Branch Manager — Deployable MVP

AI front-office and revenue-recovery system for home-service businesses.

## Run

```bash
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Dashboard: http://127.0.0.1:8000/dashboard
API docs: http://127.0.0.1:8000/docs

## Create a lead

```bash
curl -X POST http://127.0.0.1:8000/api/leads -H "Content-Type: application/json" -d '{"name":"Ravi","phone":"+919876543210","message":"My AC is not cooling","address":"12 MG Road","service":"hvac","source":"google_ads","estimated_value":450}'
```

## Production checklist

- Add Twilio credentials and webhook signature validation.
- Replace MockBookingService with Jobber, Housecall Pro, or ServiceTitan.
- Add authentication, encryption, audit logs, monitoring, backups, and rate limits.
- Add call-recording consent, privacy policy, retention rules, and AI disclosure.
