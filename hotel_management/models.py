from sqlalchemy import Integer, Column, ForeignKey, String, Boolean, Date, Float
from sqlalchemy.orm import relationship
from .database import Base

class Hotel(Base):
    __tablename__ = "hotels"

    id = Column(Integer, primary_key=True, index=True)
    hotel_name = Column(String, index=True)
    location = Column(String, index=True)
    email = Column(String, index=True)
    phone = Column(Integer, index = True)
    ratings = Column(Float, index=True)
    rooms = relationship("Room", back_populates="hotel")
    reviews = relationship("Review", back_populates="hotel")

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(Integer, index=True)
    type = Column(String, index=True)
    availability = Column(Boolean, index=True)
    price_per_day = Column(Integer, index=True)
    capacity = Column(Integer, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"))
    hotel = relationship("Hotel", back_populates="rooms")
    bookings = relationship("Booking", back_populates="room")
    

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, index=True)
    phone = Column(Integer, index=True)
    email = Column(String, index=True)
    address = Column(String, index=True)
    bookings = relationship("Booking", back_populates="customer")
    reviews = relationship("Review", back_populates="customer")

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    booking_status = Column(Boolean, index=True)
    check_in_date = Column(Date, index=True)
    check_out_date = Column(Date, index=True)
    customer_id = Column(Integer,ForeignKey("customers.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))
    total_amount = Column(Integer, index=True)
    customer = relationship("Customer", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")
    payment = relationship("Payment", back_populates="booking", uselist=False)

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"))
    payment_method = Column(String, index=True)
    payment_status = Column(Boolean, index=True)
    amount = Column(Integer, index=True)
    date_of_payment = Column(Date, index=True)
    booking = relationship("Booking", back_populates="payment")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    hotel_id = Column(Integer, ForeignKey("hotels.id"))
    ratings = Column(Float, index=True)
    review_date = Column(Date, index=True)
    customer = relationship("Customer", back_populates="reviews")
    hotel = relationship("Hotel", back_populates="reviews")