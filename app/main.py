from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, database
from datetime import date, timedelta, datetime

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/subscriptions/", response_model=schemas.Subscription)
def create_subscription(subscription: schemas.SubscriptionCreate, db: Session = Depends(get_db)):
    db_subscription = models.Subscription(
        name=subscription.name,
        price=subscription.price,
        renewal_date=subscription.renewal_date,
        frequency=subscription.frequency
    )
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription

@app.get("/")
def read_root():
    return {"message": "Subscription Tracker is Active!"}

# "READ" ENDPOINT (GET)
# This function listens for a GET request and returns a list of subscriptions.
@app.get("/subscriptions/", response_model=list[schemas.Subscription])
def read_subscriptions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    subscriptions = db.query(models.Subscription).offset(skip).limit(limit).all()
    return subscriptions

# "DELETE" ENDPOINT
@app.delete("/subscriptions/{subscription_id}")
def delete_subscription(subscription_id: int, db: Session = Depends(get_db)):
    db_subscription = db.query(models.Subscription).filter(models.Subscription.id == subscription_id).first()
    if db_subscription is None:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # 3. Delete it
    db.delete(db_subscription)
    db.commit()
    return {"message": "Subscription deleted successfully"}


# SUBSCRIPTION LOGIC AND ANALYTICS ENDPOINT
@app.get("/analytics/", response_model=schemas.AnalyticsResponse)
def get_analytics(db: Session = Depends(get_db)):
    subscriptions = db.query(models.Subscription).all()
    
    total_monthly_cost = 0.0
    
    for sub in subscriptions:
        if sub.frequency == "Monthly":
            total_monthly_cost += sub.price 
        elif sub.frequency == "Yearly":
            total_monthly_cost += (sub.price / 12) 
        elif sub.frequency == "Weekly":
             total_monthly_cost += (sub.price * 4)

    return {
        "monthly_total": round(total_monthly_cost, 2),
        "yearly_total": round(total_monthly_cost * 12, 2)
    }


# UPCOMING BILLS ENDPOINT
@app.get("/upcoming_bills/", response_model=list[schemas.Subscription])
def get_upcoming_bills(db: Session = Depends(get_db)):
    subscriptions = db.query(models.Subscription).all()
    
    upcoming = []
    today = date.today()
    
    for sub in subscriptions:
        diff =  (sub.renewal_date - today).days
        if diff >= 0 and diff <= 7:
            upcoming.append(sub)
            
    return upcoming