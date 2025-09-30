from pydantic import BaseModel
from datetime import date
from typing import Optional

class ExpenseBase(BaseModel):
    user_id: int
    amount: float
    category: str
    description: Optional[str] = None
    date: date

class ExpenseCreate(ExpenseBase):
    pass

class Expense(ExpenseBase):
    id: int
    
    class Config:
        from_attributes = True

class IncomeBase(BaseModel):
    user_id: int
    amount: float
    source: str
    description: Optional[str] = None
    date: date

class IncomeCreate(IncomeBase):
    pass

class Income(IncomeBase):
    id: int
    
    class Config:
        from_attributes = True
