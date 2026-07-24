from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated, Optional
from . database import sessionLocal, engine
from . import models
from sqlalchemy.orm import Session
from datetime import date, time

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

class RestaurantBase(BaseModel):
    name:str
    address:str
    opening_time:time
    closing_time:time
    is_open:bool

class MenuBase(BaseModel):
    name:str
    category:str
    origin:str
    price:int
    restaurant_id:int
    description:str
    availability:bool

class CustomerBase(BaseModel):
    name:str
    address:str
    phone:int
    email:str

class OrderBase(BaseModel):
    customer_id:int
    restaurant_id:int
    total_amount:int
    status:str
    order_date:date

class OrderItemBase(BaseModel):
    order_id: int
    food_id: int
    quantity: int
    price: int

class Delivery_agentBase(BaseModel):
    name:str
    phone:int
    rating:float

class CartBase(BaseModel):
    food_id:int
    quantity:int
    customer_id:int

class PaymentBase(BaseModel):
    type:str
    date:date
    status:str
    order_id:int

class ReviewBase(BaseModel):
    customer_id: int
    order_id: int
    restaurant_rating: float
    food_rating: float
    delivery_rating: float
    comment: str