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
    email:str
    phone:int
    ratings:float

class RoomBase(BaseModel):
    room_number:int
    hotel_id:int
    room_type:str
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

class PaymentBase(BaseModel):
    booking_id:int
    payment_method:str
    payment_status:bool
    amount:int
    date_of_payment:date

class ReviewBase(BaseModel):
    customer_id:int
    hotel_id:int
    ratings:float
    review_date:date

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.post("/hotels/")
async def create_hotels(hotel:HotelBase, db:db_dependency):
    db_hotel = models.Hotel(hotel_name=hotel.hotel_name, location=hotel.location,
                            email=hotel.email, phone=hotel.phone,
                            ratings=hotel.ratings)
    db.add(db_hotel)
    db.commit()
    db.refresh(db_hotel)
    return db_hotel

@app.post("/rooms/")
async def create_rooms(room:RoomBase, db:db_dependency):
    db_hotel = db.query(models.Hotel).filter(models.Hotel.id == room.hotel_id).first()
    if db_hotel is None:
        raise HTTPException(status_code=404, detail="hotel not found")
        
    db_room = models.Room(room_number=room.room_number, hotel_id=room.hotel_id, room_type=room.room_type,
                           availability=room.availability, price_per_day=room.price_per_day, capacity=room.capacity)
    
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

@app.post("/customers/")
async def create_customers(customer:CustomerBase, db:db_dependency):
    db_customer = models.Customer(customer_name=customer.customer_name, phone=customer.phone,
                                  email=customer.email, address=customer.address)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

@app.post("/bookings/")
async def create_bookings(booking:BookingBase, db:db_dependency):
    db_customer = db.query(models.Customer).filter(models.Customer.id == booking.customer_id).first()
    if db_customer is None:
        raise HTTPException(status_code=404, detail="customer not found")
    
    db_room = db.query(models.Room).filter(models.Room.id == booking.room_id).first()
    if db_room is None:
        raise HTTPException(status_code=404, detail="room not found")
    if not db_room.availability:
        raise HTTPException(status_code=400, detail="This room is already occupied")
    if booking.check_out_date <= booking.check_in_date:
        raise HTTPException(status_code=400,detail="Check-out date must be after check-in date.")
    
    days = (booking.check_out_date - booking.check_in_date).days
    total_amount = days * db_room.price_per_day
        
    db_booking = models.Booking(booking_status=booking.booking_status, check_in_date=booking.check_in_date,
                                check_out_date=booking.check_out_date, customer_id=booking.customer_id,
                                room_id=booking.room_id, total_amount=total_amount)
    
    db_room.availability = False
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    db.refresh(db_room)
    return db_booking

@app.post("/payments/")
async def create_payments(payment:PaymentBase, db:db_dependency):
    db_booking = db.query(models.Booking).filter(models.Booking.id == payment.booking_id).first()
    if db_booking is None:
        raise HTTPException(status_code=404, detail="bookings not found")        
    
    db_payment = models.Payment(booking_id=payment.booking_id, payment_method=payment.payment_method,
                                payment_status=payment.payment_status, amount=payment.amount,
                                date_of_payment=payment.date_of_payment)
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

@app.post("/reviews/")
async def create_reviews(review:ReviewBase, db:db_dependency):
    db_customer = db.query(models.Customer).filter(models.Customer.id == review.customer_id).first()
    if db_customer is None:
        raise HTTPException(status_code=404, detail="customer not found")
    
    db_hotel = db.query(models.Hotel).filter(models.Hotel.id == review.hotel_id).first()
    if db_hotel is None:
        raise HTTPException(status_code=404, detail="hotel not found")
    
    db_review = models.Review(customer_id=review.customer_id, hotel_id=review.hotel_id,
                              ratings=review.ratings, review_date=review.review_date)
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

@app.get("/hotels/{hotel_id}")
async def get_hotels(hotel_id:int, db:db_dependency):
    result = db.query(models.Hotel).filter(models.Hotel.id == hotel_id).first()
    if result is None:
        raise HTTPException(status_code=404, detail="no hotels found on this id")
    return result

@app.get("/hotels")
async def get_hotels(db:db_dependency):
    result = db.query(models.Hotel).all()
    if len(result) == 0:
        raise HTTPException(status_code=404, detail=" no hotels found")
    return result

@app.get("/rooms/{room_id}")
async def get_rooms(room_id:int, db:db_dependency):
    result = db.query(models.Room).filter(models.Room.id == room_id).first()
    if result is None:
        raise HTTPException(status_code=404, detail="no rooms found on this id")
    return result

@app.get("/rooms")
async def get_available_rooms(db:db_dependency):
    result = db.query(models.Room).all()
    if len(result) == 0:
        raise HTTPException(status_code=404, detail=" no rooms found")
    return result


@app.get("/customers/{customer_id}")
async def get_customer(customer_id:int, db:db_dependency):
    result = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if result is None:
        raise HTTPException(status_code=404, detail="customer not found ")
    return result

@app.get("/customers")
async def get_customer_details(db:db_dependency):
    result = db.query(models.Customer).all()
    if len(result) == 0:
        raise HTTPException(status_code=404, detail=" no customers found")
    return result


@app.get("/bookings/{booking_id}")
async def get_bookings(booking_id:int, db:db_dependency):
    result = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if result is None:
        raise HTTPException(status_code=404, detail="booking not found")
    return result

@app.get("/payments/{payment_id}")
async def get_payments(payment_id:int, db:db_dependency):
    result = db.query(models.Payment).filter(models.Payment.id == payment_id).first()
    if result is None:
        raise HTTPException(status_code=404, detail="no payment details found on this id")
    return result

@app.get("/reviews/{review_id}")
async def get_reviews(review_id:int, db:db_dependency):
    result = db.query(models.Review).filter(models.Review.id == review_id).first()
    if result is None:
        raise HTTPException(status_code=404, detail="no reviews from this id")
    return result

