import os
from dotenv import load_dotenv
load_dotenv()
class Settings:
    app_env=os.getenv("APP_ENV","development")
    database_url=os.getenv("DATABASE_URL","sqlite:///./ai_branch_manager.db")
    public_base_url=os.getenv("PUBLIC_BASE_URL","http://localhost:8000")
    twilio_account_sid=os.getenv("TWILIO_ACCOUNT_SID","")
    twilio_auth_token=os.getenv("TWILIO_AUTH_TOKEN","")
    twilio_phone_number=os.getenv("TWILIO_PHONE_NUMBER","")
    twilio_validate_signature=os.getenv("TWILIO_VALIDATE_SIGNATURE","false").lower()=="true"
    openai_api_key=os.getenv("OPENAI_API_KEY","")
    openai_model=os.getenv("OPENAI_MODEL","gpt-4o-mini")
settings=Settings()
