from sqlalchemy import String, Column, Integer, ForeignKey, Boolean, Date, Float, Time
from sqlalchemy.orm import relationship
from . database import Base

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String, index=True)
    opening_time = Column(Time, index=True)
    closing_time = Column(Time, index=True)
    is_open = Column(Boolean, index=True)

class Menu(Base):
    __tablename__ = "menu"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String, index=True)
    origin = Column(String, index=True)
    price = Column(String, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    description = Column(String, index=True)
    availability = Column(Boolean, index=True)

class Customer(Base):
    __tablename__ = "customer_details"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String, index=True)
    phone = Column(Integer, index=True)
    email = Column(String, index=True)

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    food_id = Column(Integer, ForeignKey("menu.id"))
    quantity = Column(Integer, index=True)
    price = Column(Integer, index=True)

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    restaurant_id = Column(Integer,ForeignKey("restaurants.id"))
    total_amount = Column(Integer, index=True)
    status = Column(String, index=True)
    order_date = Column(Date, index=True)

class Delivery_agent(Base):
    __tablename__ = "delivery_agents_list"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phone = Column(Integer, index=True)
    rating = Column(Float, index=True)

class Cart(Base):
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, index=True)
    food_id = Column(Integer, ForeignKey("menu.id"))
    quantity = Column(Integer, index=True)
    Customer_id = Column(Integer, ForeignKey("customer_details.id"))

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, index=True)
    date = Column(Date, index=True)
    status = Column(String, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customer_details.id"))
    order_id = Column(Integer, ForeignKey("orders.id"))
    restaurant_rating = Column(Float, index=True)
    food_rating = Column(Float, index=True)
    delivery_rating = Column(Float, index=True)
    comment = Column(String, index=True)