from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from typing import List, Optional
import models, schemas, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Finance Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/expenses/", response_model=schemas.Expense)
def create_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    db_expense = models.Expense(**expense.dict())
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

@app.get("/expenses/", response_model=List[schemas.Expense])
def get_expenses(
    user_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Expense).filter(models.Expense.user_id == user_id)
    
    if start_date:
        query = query.filter(models.Expense.date >= start_date)
    if end_date:
        query = query.filter(models.Expense.date <= end_date)
    if category:
        query = query.filter(models.Expense.category == category)
    
    return query.order_by(models.Expense.date.desc()).all()

@app.get("/stats/by-category/")
def get_stats_by_category(user_id: int, days: int = 30, db: Session = Depends(get_db)):
    start_date = datetime.now() - timedelta(days=days)
    result = db.query(
        models.Expense.category,
        func.sum(models.Expense.amount).label('total'),
        func.count(models.Expense.id).label('count')
    ).filter(
        models.Expense.user_id == user_id,
        models.Expense.date >= start_date
    ).group_by(models.Expense.category).all()
    
    return [{"category": r.category, "total": float(r.total), "count": r.count} for r in result]

@app.get("/stats/daily/")
def get_daily_stats(user_id: int, days: int = 30, db: Session = Depends(get_db)):
    start_date = datetime.now() - timedelta(days=days)
    result = db.query(
        models.Expense.date,
        func.sum(models.Expense.amount).label('total')
    ).filter(
        models.Expense.user_id == user_id,
        models.Expense.date >= start_date
    ).group_by(models.Expense.date).order_by(models.Expense.date).all()
    
    return [{"date": str(r.date), "total": float(r.total)} for r in result]

@app.get("/stats/monthly/")
def get_monthly_stats(user_id: int, db: Session = Depends(get_db)):
    result = db.query(
        extract('year', models.Expense.date).label('year'),
        extract('month', models.Expense.date).label('month'),
        func.sum(models.Expense.amount).label('total')
    ).filter(
        models.Expense.user_id == user_id
    ).group_by('year', 'month').order_by('year', 'month').all()
    
    return [{"year": int(r.year), "month": int(r.month), "total": float(r.total)} for r in result]

@app.get("/stats/summary/")
def get_summary(user_id: int, db: Session = Depends(get_db)):
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    today_total = db.query(func.sum(models.Expense.amount)).filter(
        models.Expense.user_id == user_id,
        models.Expense.date == today
    ).scalar() or 0
    
    week_total = db.query(func.sum(models.Expense.amount)).filter(
        models.Expense.user_id == user_id,
        models.Expense.date >= week_ago
    ).scalar() or 0
    
    month_total = db.query(func.sum(models.Expense.amount)).filter(
        models.Expense.user_id == user_id,
        models.Expense.date >= month_ago
    ).scalar() or 0
    
    return {
        "today": float(today_total),
        "week": float(week_total),
        "month": float(month_total)
    }

@app.get("/categories/")
def get_categories(db: Session = Depends(get_db)):
    result = db.query(models.Expense.category).distinct().all()
    return [r.category for r in result]

@app.post("/income/", response_model=schemas.Income)
def create_income(income: schemas.IncomeCreate, db: Session = Depends(get_db)):
    db_income = models.Income(**income.dict())
    db.add(db_income)
    db.commit()
    db.refresh(db_income)
    return db_income

@app.get("/balance/")
def get_balance(user_id: int, db: Session = Depends(get_db)):
    total_income = db.query(func.sum(models.Income.amount)).filter(
        models.Income.user_id == user_id
    ).scalar() or 0
    
    total_expenses = db.query(func.sum(models.Expense.amount)).filter(
        models.Expense.user_id == user_id
    ).scalar() or 0
    
    return {
        "income": float(total_income),
        "expenses": float(total_expenses),
        "balance": float(total_income - total_expenses)
    }

