from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Annotated, List, Optional
from . database import engine, SessionLocal
from . import models
from sqlalchemy.orm import Session
from datetime import date

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

class HotelBase(BaseModel):
    hotel_name:str
    location:str
    emial:str
    phone:int
    ratings:float

class RoomBase(BaseModel):
    room_number:int
    type:str
    availability:bool
    price_per_day:int
    capacity:int

class CustomerBase(BaseModel):
    customer_name:str
    phone:int
    email:str
    address:str

class BookingBase(BaseModel):
    booking_status:bool
    check_in_date:date
    check_out_date:date
    customer_id:int
    room_id:int
    total_amount:int

class paymentBase(BaseModel):
    booking_id:int
    payment_method:str
    payment_status:bool
    amount:int
    date_of_payment:date

class reviewBase(BaseModel):
    customer_id:int
    hotel_id:int
    rating:float
    review_date:date