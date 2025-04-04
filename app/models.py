from sqlalchemy import Column, Integer, String, Text

from app.database import Base


class Recipe(Base):
    __tablename__ = "recipe"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    ingredients = Column(Text)
    cooking_process = Column(Text)
    cooking_time = Column(Integer, index=True)
    rating = Column(Integer, default=0)
