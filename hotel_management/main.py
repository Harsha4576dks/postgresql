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

class UpdateRoom(BaseModel):
    room_number:Optional[int]  = None
    room_type:Optional[str] = None
    availability:Optional[bool] = None
    price_per_day:Optional[int] = None
    capacity:Optional[int] = None

class UpdateCustomer(BaseModel):
    customer_name:Optional[str] = None
    phone:Optional[int] = None
    email:Optional[str] = None
    address:Optional[str] = None

class UpdateBooking(BaseModel):
    booking_status:Optional[bool]  = None
    check_in_date:Optional[date] = None
    check_out_date:Optional[date] = None
    customer_id:Optional[int] = None
    room_id:Optional[int] = None

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

@app.patch("/rooms/{room_id}")
async def update_room_details(room_id:int, room:UpdateRoom, db:db_dependency):
    db_room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if db_room is None:
        raise HTTPException(status_code=404, detail="room not found")
    
    update_data = room.model_dump(exclude_unset=True)
    print(update_data)
    for key, value in update_data.items():
        setattr(db_room, key, value)

    db.commit()
    db.refresh(db_room)
    return db_room

@app.patch("/customers/{customer_id}")
async def update_customer_details(customer_id:int, customer:UpdateCustomer, db:db_dependency):
    db_customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if db_customer is None:
        raise HTTPException(status_code=404, detail="customer not found")
    
    update_data = customer.model_dump(exclude_unset=True)
    print(update_data)
    for key, value in update_data.items():
        setattr(db_customer, key, value)

    db.commit()
    db.refresh(db_customer)
    return db_customer
 
@app.patch("/bookings/{booking_id}")
async def update_booking_details(booking_id: int, booking: UpdateBooking, db: db_dependency):
    db_booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if db_booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.customer_id is not None:
        db_customer = db.query(models.Customer).filter(models.Customer.id == booking.customer_id).first()
        if db_customer is None:
            raise HTTPException(status_code=404, detail="Customer not found")

    if booking.room_id is not None:
        db_room = db.query(models.Room).filter(models.Room.id == booking.room_id).first()
        if db_room is None:
            raise HTTPException(status_code=404, detail="Room not found")
        if not db_room.availability:
            raise HTTPException(status_code=400,detail="Room is already occupied")

    update_data = booking.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_booking, key, value)

    if db_booking.check_out_date <= db_booking.check_in_date:
        raise HTTPException(status_code=400,detail="Check-out date must be after check-in date.")

    db_room = db.query(models.Room).filter(models.Room.id == db_booking.room_id).first()

    days = (db_booking.check_out_date - db_booking.check_in_date).days
    db_booking.total_amount = days * db_room.price_per_day

    if db_booking.booking_status in ["Cancelled", "Completed"]:
        db_room.availability = True

    db.commit()
    db.refresh(db_booking)
    return db_booking

@app.delete("/hotel/{hotel_id}")
async def delete_hotel(hotel_id:int, db:db_dependency):
    db_hotel = db.query(models.Hotel).filter(models.Hotel.id == hotel_id).first()
    if db_hotel is None:
        raise HTTPException(status_code=404, detail="hotel not found")
    
    db_rooms =  db.query(models.Room).filter(models.Room.hotel_id == hotel_id).all()
    if db_rooms:
        raise HTTPException(status_code=400, detail="delete all the rooms belonging to this hotel first")
   
    db.delete(db_hotel)
    db.commit()
    return {"message":"This hotel details is successfully deleted", "deleted_hotel":hotel_id}

@app.delete("/rooms/{room_id}")
async def delete_rooms(room_id:int, db:db_dependency):
    db_room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if db_room is None:
            raise HTTPException(status_code=404, detail="rooms not found")
    
    db_booking = db.query(models.Booking).filter(models.Booking.room_id == room_id).all()
    if db_booking:
        raise HTTPException(status_code=400, detail="This room is having a booking, so delete the booking first")
    
    db.delete(db_room)
    db.commit()
    return {"message":"room deleted successfully", "deleted_room":room_id}

@app.delete("/bookings/{booking_id}")
async def delete_booking(booking_id:int, db:db_dependency):
    db_booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if db_booking is None:
        raise HTTPException(status_code=404, detail="no bookings found")
    
    db_payment = db.query(models.Payment).filter(models.Payment.booking_id == booking_id).all()
    if db_payment:
        raise HTTPException(status_code=400, detail="cancel the payments on this room and refund")
    
    db.delete(db_booking)
    db.commit()
    return {"message":"bookings successfully deleted", "deleted_booking":booking_id}

@app.delete("/customer/{customer_id}")
async def delete_customer(customer_id:int, db:db_dependency):
    db_booking = db.query(models.Booking).filter(models.Booking.customer_id == customer_id).first()
    if db_booking:
        raise HTTPException(status_code=400,detail="Delete customer's bookings first")
    db_customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if db_customer is None:
        raise HTTPException(status_code=404, detail="customer not found")
    
    db.delete(db_customer)
    db.commit()
    return {"message":"customer details deleted successfully", "deleted_customer":customer_id}

@app.delete("/payments/{payment_id}")
async def delete_payments(payment_id:int, db:db_dependency):
    db_payment = db.query(models.Payment).filter(models.Payment.id == payment_id).first()
    if db_payment is None:
        raise HTTPException(status_code=404, detail="payment not found")
    
    db.delete(db_payment)
    db.commit()
    return {"message":"payment details deleted successfully", "deleted_payment":payment_id}

@app.delete("/reviews/{review_id}")
async def delete_review(review_id:int, db:db_dependency):
    db_review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if db_review  is None:
        raise HTTPException(status_code=404, detail="review not found")
    
    db.delete(db_review)
    db.commit()
    return {"message":"review details deleted successfully", "deleted_review":db_review.id}
