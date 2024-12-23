from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Animal, TypeAnimal


# ############################ Категории животных ######################################


async def orm_get_types_animal(session: AsyncSession):
    query = select(TypeAnimal)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_private_types_animal(session: AsyncSession):
    query = select(TypeAnimal)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_update_types_animal(session: AsyncSession, types_animal_id: int, data):
    query = (
        update(TypeAnimal)
        .where(TypeAnimal.type_animal_id == types_animal_id)
        .values(
            animal=data["animal"]
        )
    )
    await session.execute(query)
    await session.commit()


async def orm_create_types_animal(session: AsyncSession, animals: list):
    query = select(TypeAnimal)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([TypeAnimal(animal=animal) for animal in animals])
    await session.commit()


async def orm_create_type_animal(session: AsyncSession, data: dict):
    obj = TypeAnimal(
        animal=data["animal"],
    )
    session.add(obj)
    await session.commit()


async def orm_delete_type_animals(session: AsyncSession, type_id: int):
    query = delete(TypeAnimal).where(TypeAnimal.type_animal_id == type_id)
    await session.execute(query)
    await session.commit()


# ############ Админка: добавить/изменить/удалить животное ########################


async def orm_add_animal(session: AsyncSession, data: dict):
    obj = Animal(
        name=data["name"],
        breed=data["breed"],
        age=int(data["age"]),
        age_bigger5=data["age_bigger5"],
        male=data["male"],
        medical_history=data["medical_history"],
        vaccinations=data["vaccinations"],
        type_animal_id=int(data["type_animal"]),
        image=data["image"]
    )
    session.add(obj)
    await session.commit()


async def orm_get_animals(session: AsyncSession, type_animal_id):
    query = select(Animal).where(Animal.type_animal_id == int(type_animal_id))
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_animal(session: AsyncSession, animal_id: int):
    query = select(Animal).where(Animal.id == animal_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_animal_cheep(session: AsyncSession, animal_id: int, type_id: int):
    query = select(Animal).where(Animal.id == animal_id, Animal.type_animal_id == type_id)
    result = await session.execute(query)
    return result.scalar()



async def orm_update_animal(session: AsyncSession, animal_id: int, data):
    query = (
        update(Animal)
        .where(Animal.id == animal_id)
        .values(
            name=data["name"],
            breed=data["breed"],
            age=int(data["age"]),
            male=data["male"],
            medical_history=data["medical_history"],
            vaccinations=data["vaccinations"],
            type_animal_id=int(data["type_animal"]),
            image=data["image"],
        )
    )
    await session.execute(query)
    await session.commit()


async def orm_delete_animal(session: AsyncSession, animal_id: int):
    query = delete(Animal).where(Animal.id == animal_id)
    await session.execute(query)
    await session.commit()


async def orm_get_breed(session: AsyncSession, type_animal_id: int):
    query = select(Animal).where(Animal.type_animal_id == type_animal_id)
    result = await session.execute(query)
    return result.scalars().all()


async def get_search_animal(session: AsyncSession, type_animal_id: int, age_bigger5: int, breed: str, male): #breed: str, age_bigger5: int, male: str
    query = select(Animal).where(Animal.type_animal_id == int(type_animal_id),
                                Animal.age_bigger5 == int(age_bigger5),
                                Animal.breed == breed,
                                Animal.male == male,
                                 )
    #

    #
    result = await session.execute(query)
    return result.scalars().all()