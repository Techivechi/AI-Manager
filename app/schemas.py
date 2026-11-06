from pydantic import BaseModel,Field
from typing import Optional
class LeadCreate(BaseModel):
 name:str=Field(min_length=1); phone:str=Field(min_length=7); message:str; address:str=""; service:str="hvac"; source:str="direct"; estimated_value:float=0
class SettingsUpdate(BaseModel):
 business_name:str; business_phone:str; emergency_phone:str; service_areas:list[str]; business_hours:str; auto_booking_enabled:bool=True
class LeadUpdate(BaseModel):
 status:Optional[str]=None; estimated_value:Optional[float]=None; escalation_reason:Optional[str]=None
