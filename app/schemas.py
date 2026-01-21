from pydantic import BaseModel
from datetime import date

class SubscriptionCreate(BaseModel):
    name: str
    price: float
    renewal_date: date
    frequency: str

class Subscription(SubscriptionCreate):
    id: int

    class Config:
        from_attributes = True

class AnalyticsResponse(BaseModel):
    monthly_total: float
    yearly_total: float

