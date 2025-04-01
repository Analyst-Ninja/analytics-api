from sqlmodel import SQLModel, Field, DateTime
from typing import List, Optional
from datetime import datetime, timezone
from timescaledb import TimescaleModel
from timescaledb.utils import get_utc_now

# We can use TimescaleDB version, it also uses it in time columns
# def get_utc_now():
#     return datetime.now(timezone.utc).replace(tzinfo=timezone.utc)

# page vistis at any given time

class EventModel(TimescaleModel, table=True):
    page: str = Field(index=True)
    user_agent: Optional[str] = Field(default="", index=True) # browser
    ip_address: Optional[str] = Field(default="", index=True)
    referrer: Optional[str] = Field(default="", index=True)
    session_id: Optional[str] = Field(index=True)
    duration: Optional[int] = Field(default=0)
    
    __chunk_time_interval__ = "INTERVAL 1 day"
    __drop_after__ = "INTERVAL 3 months"

class EventListSchema(SQLModel):
    result: List[EventModel]
    count: int

class EventCreateSchema(SQLModel):
    page: str
    user_agent: Optional[str] = Field(default="", index=True) # browser
    ip_address: Optional[str] = Field(default="", index=True)
    referrer: Optional[str] = Field(default="", index=True)
    session_id: Optional[str] = Field(index=True)
    duration: Optional[int] = Field(default=0)

# We are not allowing UPDATE here --> Hence commenting out
# class EventUpdateSchema(SQLModel):
#     description: str

class EventBucketSchema(SQLModel):
    bucket: datetime
    page: str
    ua: Optional[str] = ""
    operating_system: Optional[str] = ""
    average_duration: Optional[float] = 0.0
    count: int

