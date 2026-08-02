from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models. No models are defined
    yet — this milestone only wires up the database layer itself."""
