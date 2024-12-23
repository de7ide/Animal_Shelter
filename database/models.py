from sqlalchemy import DateTime, ForeignKey, String, func, Integer, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class TypeAnimal(Base):
    __tablename__ = 'type_animal'

    type_animal_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    animal: Mapped[str] = mapped_column(String(150), nullable=False)


class Animal(Base):
    __tablename__ = 'animal'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type_animal_id: Mapped[int] = mapped_column(ForeignKey('type_animal.type_animal_id', ondelete='CASCADE'), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    breed: Mapped[str] = mapped_column(String(150), nullable=False)
    age: Mapped[str] = mapped_column(Integer())
    age_bigger5: Mapped[int] = mapped_column(Integer(), nullable=False)
    male: Mapped[str] = mapped_column(String(20))
    medical_history: Mapped[str] = mapped_column(String())
    vaccinations: Mapped[str] = mapped_column(String())
    image: Mapped[str] = mapped_column(String(), nullable=True)

    type_animal: Mapped['TypeAnimal'] = relationship(backref='type_animal')
