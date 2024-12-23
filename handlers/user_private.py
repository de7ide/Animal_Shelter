from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_query import (
    orm_get_private_types_animal,
    orm_get_animals,
    orm_get_animal,
    orm_get_animal_cheep,
    orm_get_breed,
    get_search_animal,
)

from filters.chat_types import ChatTypeFilter
from kbds.inline import get_callback_btns


user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))


class SearchAnimal(StatesGroup):
    wait = State()
    cheap = State()
    individual_search = State()


@user_private_router.message(CommandStart())
@user_private_router.message(Command('search'))
async def start_command(message: Message, session: AsyncSession, state: FSMContext):
    await state.clear()
    types = await orm_get_private_types_animal(session)
    btns = {type_animal.animal : f'type_animal_{type_animal.type_animal_id}' for type_animal in types}
    await message.answer("Выберите категорию", reply_markup=get_callback_btns(btns=btns))
    await state.set_state(SearchAnimal.wait)


@user_private_router.callback_query(SearchAnimal.wait, F.data.startswith('type_animal_'))
async def callback_type_animal(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    type_id = callback.data.split('_')[-1]
    await state.update_data(type_animal=int(type_id))
    types = await orm_get_animals(session, type_animal_id=type_id)
    btns = {str(animal.id) : f'animal_{animal.id}' for animal in types}
    dop_btns = {'🔍 Ввести чип': 'search_cheep','Поиск по характеристикаи' : 'search_individual', '◀️ Назад' : 'back_button_type'}
    btns = {**btns, **dop_btns}
    await callback.message.edit_text(text='<b>Выберите чип животного:</b>', reply_markup=get_callback_btns(btns=btns, sizes=(1,)))


# @user_private_router.callback_query(SearchAnimal.wait, F.data.startswith('type_animal_'))


@user_private_router.callback_query(SearchAnimal.wait, F.data == 'back_button_type')
async def back_to_start_command(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    types = await orm_get_private_types_animal(session)
    btns = {type_animal.animal : f'type_animal_{type_animal.type_animal_id}' for type_animal in types}
    await callback.message.edit_text("Выберите категорию", reply_markup=get_callback_btns(btns=btns))


@user_private_router.callback_query(SearchAnimal.wait, F.data.startswith('animal_'))
async def calback_animal(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    animal_id = callback.data.split('_')[-1]
    animal = await orm_get_animal(session, animal_id=int(animal_id))
    # await callback.message.edit_text(
    #         text=f"<b>Номер чипа:</b> {animal.id}\n<b>Порода: </b>{animal.breed}\
    #                 \n<b>Возраст: </b>{animal.age}\n<b>Пол:</b> {animal.male}\
    #                 \n\n<b>Медицинская история:</b>\n {animal.medical_history}\
    #                 \n\n<b>Вакцины:</b> \n {animal.vaccinations}",
    #         reply_markup=get_callback_btns(btns={'◀️ Назад': f'back_button_cheap_{animal.type_animal_id}'}))
    if animal.image != 'None':
            await callback.message.answer_photo(
                photo=animal.image,
                caption=f"<b>Номер чипа:</b> {animal.id}\n<b>Кличка: </b>{animal.name}<b>\nПорода: </b>{animal.breed}\
                        \n<b>Возраст: </b>{animal.age}\n<b>Пол:</b> {animal.male}\
                        \n\n<b>Медицинская история:</b>\n {animal.medical_history}\
                        \n\n<b>Вакцины:</b>\n{animal.vaccinations}",


            )
    else:
        await callback.message.answer(
            text=f"<b>Номер чипа:</b> {animal.id}\n<b>Кличка: </b>{animal.name}\n<b>Порода: </b>{animal.breed}\
                    \n<b>Возраст: </b>{animal.age}\n<b>Пол:</b> {animal.male}\
                    \n\n<b>Медицинская история:</b>\n {animal.medical_history}\
                    \n\n<b>Вакцины:</b>\n{animal.vaccinations}",

        )


@user_private_router.callback_query(SearchAnimal.wait, F.data.startswith('back_button_cheap'))
async def back_button_cheap(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    type_id = callback.data.split('_')[-1]
    await state.update_data(type_animal=int(type_id))
    types = await orm_get_animals(session, type_animal_id=type_id)
    btns = {str(animal.id) : f'animal_{animal.id}' for animal in types}
    dop_btns = {'🔍 Ввести чип': 'search_cheep', '◀️ Назад' : 'back_button_type'}
    btns = {**btns, **dop_btns}
    await callback.message.edit_text(text='<b>Выберите чип животного:</b>', reply_markup=get_callback_btns(btns=btns, sizes=(1,)))


@user_private_router.callback_query(SearchAnimal.wait, F.data == 'search_individual')
async def search_individual(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    await state.set_state(SearchAnimal.individual_search)
    data = await state.get_data()
    types_bredd = await orm_get_breed(session, data['type_animal'])
    btns = {animal.breed : f"animal_breed_{animal.breed}" for animal in types_bredd}
    await callback.message.edit_text(
        text='Выберите породу:',
        reply_markup=get_callback_btns(btns=btns)
    )


@user_private_router.callback_query(SearchAnimal.individual_search, F.data.startswith('animal_breed_'))
async def age_bigger5(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    callback_breed = callback.data.split('_')[-1]
    await state.update_data(breed=callback_breed)
    await callback.message.edit_text(
        text='Выберите диапазон возрата: ',
        reply_markup=get_callback_btns(btns={'Больше 5 лет' : 'age_bigger_1', 'Меньше 5 лет': 'age_smaller_0'})
    )


@user_private_router.callback_query(SearchAnimal.individual_search, F.data.startswith('age_'))
async def male_choose(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    callback_age_sravni = callback.data.split('_')[-1]
    await state.update_data(age_bigger5=int(callback_age_sravni))
    await callback.message.edit_text(
        text='Выберите желаемый пол животного: ',
        reply_markup=get_callback_btns(btns={'Мужcкой': 'Мужской', 'Женский' : 'Женский'})
    )


@user_private_router.callback_query(SearchAnimal.individual_search, F.data.endswith('й'))
async def itog_search(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    await state.update_data(male=callback.data)
    data = await state.get_data()
    print(data["type_animal"], data["breed"], data["age_bigger5"], data["male"])
    types = await get_search_animal(session, data["type_animal"], data["age_bigger5"], data["breed"], data["male"])
    print(types)
    print(data)


    btns = {str(animal.id) : f'cheap_search_{animal.id}' for animal in types}
    print(btns)
    await callback.message.edit_text(
        text='Чипы животных, удовлетворяющие ваши требования:',
        reply_markup=get_callback_btns(btns=btns)
    )
    await state.set_state(SearchAnimal.cheap)



@user_private_router.callback_query(F.data == 'search_cheep')
async def cheap_search(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    await callback.message.edit_text('<b>Введите чип</b>')
    await state.set_state(SearchAnimal.cheap)


@user_private_router.callback_query(SearchAnimal.cheap, F.data.startswith('cheap_search_'))
async def search_cheap_callback(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    await state.update_data(cheap=int(callback.data.split('_')[-1]))
    data = await state.get_data()
    info = await orm_get_animal_cheep(session, data['cheap'], data['type_animal'])
    if info.image != 'None':
            await callback.message.answer_photo(
                photo=info.image,
                caption=f"<b>Номер чипа:</b> {info.id}\n<b>Кличка: </b>{info.name}\n<b>Порода: </b>{info.breed}\
                        \n<b>Возраст: </b>{info.age}\n<b>Пол:</b> {info.male}\
                        \n\n<b>Медицинская история:</b>\n {info.medical_history}\
                        \n\n<b>Вакцины:</b>\n{info.vaccinations}",
            )
    else:
        await callback.message.answer(
            text=f"<b>Номер чипа:</b> {info.id}\n<b>Кличка: </b>{info.name}\n<b>Порода: </b>{info.breed}\
                    \n<b>Возраст: </b>{info.age}\n<b>Пол:</b> {info.male}\
                    \n\n<b>Медицинская история:</b>\n {info.medical_history}\
                    \n\n<b>Вакцины:</b>\n{info.vaccinations}",

        )
    await callback.answer()
    await state.clear()


@user_private_router.message(SearchAnimal.cheap, F.text.isdigit())
async def search_cheap(message: Message, session: AsyncSession, state: FSMContext):
    await state.update_data(cheap=int(message.text))
    data = await state.get_data()
    info = await orm_get_animal_cheep(session, data['cheap'], data['type_animal'])
    if info:
        if info.image != 'None':
            await message.answer_photo(
                photo=info.image,
                caption=f"<b>Номер чипа:</b> {info.id}\n<b>Кличка: </b>{info.name}\n<b>Порода: </b>{info.breed}\
                        \n<b>Возраст: </b>{info.age}\n<b>Пол:</b> {info.male}\
                        \n\n<b>Медицинская история:</b>\n {info.medical_history}\
                        \n\n<b>Вакцины:</b>\n{info.vaccinations}",
            )
        else:
            await message.answer(
                text=f"<b>Номер чипа:</b> {info.id}\n<b>Кличка: </b>{info.name}\n<b>Порода: </b>{info.breed}\
                        \n<b>Возраст: </b>{info.age}\n<b>Пол:</b> {info.male}\
                        \n\n<b>Медицинская история:</b>\n {info.medical_history}\
                        \n\n<b>Вакцины:</b>\n{info.vaccinations}",
            )
    await state.clear()


@user_private_router.message(SearchAnimal.cheap)
async def error_search(message: Message):
    await message.answer('<b>Ничего не найдено(Убедитетесь что чип введен корректно...)</b>')
