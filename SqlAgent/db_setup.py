import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Get the SQLite database url from the environment variable
SQLALCHEMY_DATABASE_URL = os.environ.get("SQLALCHEMY_DATABASE_URL")

# Create the SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the base class for declarative models
Base = declarative_base()

# User Model
class User(Base):
    """
    User model representing a user in the database.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    age = Column(Integer)

    # Relationship with Order model
    orders = relationship("Order", back_populates="user")

class Food(Base):
    """
    Food model representing a food item in the database.
    """
    __tablename__ = "foods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)

    # Relationship with Order model
    orders = relationship("Order", back_populates="food")

class Order(Base):
    """
    Order model representing an order in the database.
    """
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    food_id = Column(Integer, ForeignKey("foods.id"))
    quantity = Column(Integer)

    # Relationships with User and Food models
    user = relationship("User", back_populates="orders")
    food = relationship("Food", back_populates="orders")


def init_db():
    """
    Initialize the database by creating all tables.
    """
    Base.metadata.create_all(bind=engine)
    print("Database initialized")
    session = SessionLocal()

    # Add some users
    users = [
        User(name="John Doe", email="john@example.com", age=25),
        User(name="Jane Smith", email="jane@example.com", age=30),
        User(name="Bob Johnson", email="bob@example.com", age=22),
    ]
    session.add_all(users)
    session.commit()

    # add some foods
    foods = [
        Food(name="Burger", price=5.99),
        Food(name="Pizza", price=8.99),
        Food(name="Salad", price=4.99),
    ]
    session.add_all(foods)
    session.commit()

    # add some orders
    orders = [
        Order(user_id=1, food_id=1, quantity=2),
        Order(user_id=1, food_id=2, quantity=1),
        Order(user_id=2, food_id=3, quantity=3),
        Order(user_id=3, food_id=1, quantity=1),
    ]
    session.add_all(orders)
    session.commit()

    session.close()
    print("Database initialized")

if __name__ == "__main__":
    # if database not exists, create & intialize the database
    if not os.path.exists("food_delivery.db"):
        print("Database does not exist, creating database...")
        init_db() 
    else:
        print("Database already exists")
   