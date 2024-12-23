from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import (
    orm_get_types_animal,
    orm_create_type_animal,
    orm_add_animal,
    orm_get_animals,
    orm_get_animal,
    orm_update_animal,
    orm_delete_animal,
    orm_delete_type_animals,
    orm_update_types_animal,
)

from filters.chat_types import ChatTypeFilter, IsAdmin

from kbds.inline import get_callback_btns
from kbds.reply import get_keyboard


admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())

#клавиатура для админ панели
ADMIN_KB = get_keyboard(
    "Добавить животное",
    "Ассортимент",
    "Добавить категорию животных",
    "Изменить категорию животных",
    placeholder="Выберите действие",
    sizes=(2,),
)

#клавиатура выбора пола
MALE_KB = get_keyboard(
    'Мужской',
    'Женский',
    placeholder='Введите пол',
    sizes=(1,),
)


#хэндлер для обработки команды /admin
#вход в админ панель
@admin_router.message(Command("admin"))
async def admin_features(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Что хотите сделать?", reply_markup=ADMIN_KB)

#обработчик кнопки "Ассортимент"
#выводит список всех имеющихся животных
@admin_router.message(F.text == 'Ассортимент')
async def admin_features(message: Message, session: AsyncSession):
    types = await orm_get_types_animal(session)
    btns = {type_animal.animal : f'type_animal_{type_animal.type_animal_id}' for type_animal in types}
    await message.answer("Выберите категорию", reply_markup=get_callback_btns(btns=btns))


class AddTypeAnimal(StatesGroup):
    wait = State()
    name = State()
    add_category = State()
    change_category = State()
    dell_category = State()


#Обработчик кнопки 'Изменить категорию животных'
@admin_router.message(StateFilter('*'), F.text == 'Изменить категорию животных')
async def list_of_animal(message: Message, session: AsyncSession, state: FSMContext):
    await state.clear()
    await state.set_state(AddTypeAnimal.wait)
    types = await orm_get_types_animal(session)
    btns = {type_animal.animal : f'type_animal_{type_animal.type_animal_id}' for type_animal in types}

    await message.answer("Выберите категорию", reply_markup=get_callback_btns(btns=btns))


#нажатие кнопки категории
@admin_router.callback_query(AddTypeAnimal.wait, F.data.startswith('type_animal_'))
async def category_animal(callback: CallbackQuery, state: FSMContext):
    type_cat = callback.data.split('_')[-1]
    await state.update_data(animal_type=type_cat)
    await callback.message.edit_text('Выберите действие:',
                                     reply_markup=get_callback_btns(btns={"Удалить": f'dell_category_{type_cat}',
                                                                        "Изменить" : 'change_category',
                                                                        "◀️ Назад" : "back_button_admin_motion"}))


#нажатие кнопки "Назад"
@admin_router.callback_query(F.data == 'back_button_admin_motion')
async def back_button_motion(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    await state.clear()
    await state.set_state(AddTypeAnimal.wait)
    types = await orm_get_types_animal(session)
    btns = {type_animal.animal : f'type_animal_{type_animal.type_animal_id}' for type_animal in types}
    await callback.message.edit_text("Выберите категорию", reply_markup=get_callback_btns(btns=btns))


#нажатие кнопки "Удалить"
@admin_router.callback_query(AddTypeAnimal.wait, F.data.startswith('dell_category'))
async def dell_category(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    cat_id = callback.data.split('_')[-1]
    await orm_delete_type_animals(session, int(cat_id))
    await state.update_data(type_id=cat_id)

    await callback.answer('Категория удалена')
    await callback.message.answer('Категория удалена')

#нажатие кнопки "Добавить категорию животных"
@admin_router.message(F.text == 'Добавить категорию животных')
async def add_category(message: Message, session: AsyncSession, state: FSMContext):
    await message.answer('Введите название категории:')
    await state.set_state(AddTypeAnimal.add_category)

#ожидание ввода названия категории
@admin_router.message(AddTypeAnimal.add_category, F.text)
async def add_cat(message: Message, session: AsyncSession, state: FSMContext):
    await state.update_data(animal=message.text)
    data = await state.get_data()
    await orm_create_type_animal(session, data)
    await message.answer('Категория добавлена')
    await state.clear()

#нажатие кнопки "Изменить"
@admin_router.callback_query(AddTypeAnimal.wait, F.data == 'change_category')
async def change_category(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    await callback.message.edit_text('Введите новое название категории:')
    await state.set_state(AddTypeAnimal.change_category)


#ожидание ввода названия категории
@admin_router.message(AddTypeAnimal.change_category, F.text)
async def change_category2(message: Message, session: AsyncSession, state: FSMContext):

    await state.update_data(animal=message.text)
    data = await state.get_data()
    print(data)
    await orm_update_types_animal(session,data["animal_type"], data)
    await message.answer('Категория обновлена')
    await state.clear()


#обработчик нажатия кнопики по категориям
@admin_router.callback_query(F.data.startswith('type_animal_'))
async def callback_type_animal(callback: CallbackQuery, session: AsyncSession):
    type_animal_id = callback.data.split('_')[-1]
    for animal in await orm_get_animals(session, int(type_animal_id)):
        if animal.image != 'None':
            await callback.message.answer_photo(
                photo=animal.image,
                caption=f"<b>Номер чипа:</b> {animal.id}\n<b>Кличка: </b>{animal.name}<b>\nПорода: </b>{animal.breed}\
                        \n<b>Возраст: </b>{animal.age}\n<b>Пол:</b> {animal.male}\
                        \n\n<b>Медицинская история:</b>\n {animal.medical_history}\
                        \n\n<b>Вакцины:</b>\n{animal.vaccinations}",
                reply_markup=get_callback_btns(
                    btns={
                        "Удалить": f"delete_{animal.id}",
                        "Изменить": f"change_{animal.id}",
                    },
                    sizes=(2,)
                ),
            )
        else:
            await callback.message.answer(
                text=f"<b>Номер чипа:</b> {animal.id}\n<b>Кличка: </b>\n{animal.name}\n<b>Порода: </b>{animal.breed}\
                        \n<b>Возраст: </b>{animal.age}\n<b>Пол:</b> {animal.male}\
                        \n\n<b>Медицинская история:</b>\n {animal.medical_history}\
                        \n\n<b>Вакцины:</b>\n{animal.vaccinations}",
                reply_markup=get_callback_btns(
                    btns={
                        "Удалить": f"delete_{animal.id}",
                        "Изменить": f"change_{animal.id}",
                    },
                    sizes=(2,)
                ),
            )

    await callback.answer()


#колбэк нажатия кнопки "Удалить"
@admin_router.callback_query(F.data.startswith("delete_"))
async def delete_product_callback(callback: CallbackQuery, session: AsyncSession):
    animal_id = callback.data.split("_")[-1]
    await orm_delete_animal(session, int(animal_id))

    await callback.answer("Животное удалено")
    await callback.message.answer("Животное удалено")


#состояния для добовления нового житоного
class AddAnimal(StatesGroup):
    name = State()
    breed = State()
    age = State()
    type_animal = State()
    male = State()
    medical_history = State()
    vaccinations = State()
    image = State()

    animal_for_change = None


# Становимся в состояние ожидания ввода name
@admin_router.callback_query(StateFilter(None), F.data.startswith("change_"))
async def change_animal_callback(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    animal_id = callback.data.split("_")[-1]

    animal_for_change = await orm_get_animal(session, int(animal_id))

    AddAnimal.animal_for_change = animal_for_change

    await callback.answer()
    await callback.message.answer(
        "Введите кличку животного:", reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AddAnimal.name)


# Становимся в состояние ожидания ввода name
@admin_router.message(StateFilter(None), F.text == "Добавить животное")
async def add_product(message: Message, state: FSMContext):
    await message.answer(
        "Введите кличку животного", reply_markup=ReplyKeyboardRemove()
    )
    await message.answer('Для отмены введите "отмена" или /cancel')
    await message.answer('Что бы вернуться на предыдущий шаг введите "назад" или /back')

    await state.set_state(AddAnimal.name)


# Хендлер отмены и сброса состояния должен быть всегда именно здесь,
# после того, как только встали в состояние номер 1 (элементарная очередность фильтров)
@admin_router.message(StateFilter("*"), Command("cancel"))
@admin_router.message(StateFilter("*"), F.text.casefold() == "отмена")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    if AddAnimal.animal_for_change:
        AddAnimal.animal_for_change = None
    await state.clear()
    await message.answer("Действия отменены", reply_markup=ADMIN_KB)


# Вернутся на шаг назад (на прошлое состояние)
@admin_router.message(StateFilter("*"), Command("back"))
@admin_router.message(StateFilter("*"), F.text.casefold() == "назад")
async def back_step_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()

    if current_state == AddAnimal.breed:
        await message.answer(
            'Предидущего шага нет, или введите породу животного или напишите "отмена"'
        )
        return

    previous = None
    for step in AddAnimal.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(
                f"Ок, вы вернулись к прошлому шагу" #\n {AddAnimal.texts[previous.state]}"
            )
            return
        previous = step


# Ловим данные для состояние name и потом меняем состояние на breed
@admin_router.message(AddAnimal.name, F.text)
async def add_name(message: Message, state: FSMContext):
    if message.text == "." and AddAnimal.animal_for_change:
        await state.update_data(name=AddAnimal.animal_for_change.name)
    else:
        if 1 > len(message.text) >= 150:
            await message.answer("Кличка не должна быть менее 1 символа\nИли быть более 150")
            return
        await state.update_data(name=message.text)
    await message.answer("Введите породу животного:")
    await state.set_state(AddAnimal.breed)


# Хендлер для отлова некорректных вводов для состояния name
@admin_router.message(AddAnimal.name)
async def add_name_erron(message: Message):
    await message.answer("Вы ввели не допустимые данные")


# Ловим данные для состояние breed и потом меняем состояние на age
@admin_router.message(AddAnimal.breed, F.text)
async def add_breed(message: Message, state: FSMContext):
    if message.text == "." and AddAnimal.animal_for_change:
        await state.update_data(breed=AddAnimal.animal_for_change.breed)
    else:
        # Здесь можно сделать какую либо дополнительную проверку
        # и выйти из хендлера не меняя состояние с отправкой соответствующего сообщения
        # например:
        if 2 >= len(message.text) >= 150:
            await message.answer(
                "Название породы не должно превышать 150 символов\nили быть менее 2 символов. \n Введите заново"
            )
            return

        await state.update_data(breed=message.text)
    await message.answer("Введите возраст(целое число)")
    await state.set_state(AddAnimal.age)

# Хендлер для отлова некорректных вводов для состояния breed
@admin_router.message(AddAnimal.breed)
async def add_error_breed(message: Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные")


# Ловим данные для состояние age и потом меняем состояние на type_animal
@admin_router.message(AddAnimal.age, lambda x: x.text.isdigit() and 0 <= int(x.text) <= 100)
async def add_age(message: Message, state: FSMContext, session: AsyncSession):
    if message.text == "." and AddAnimal.animal_for_change:
        await state.update_data(age=AddAnimal.animal_for_change.age)
    else:
        if 0 > int(message.text):
            await message.answer(
                "Слишком коротко. \n Введите заново"
            )
            return
        await state.update_data(age=message.text)

    if int(message.text) > 5:
        await state.update_data(age_bigger5=1)
    else:
        await state.update_data(age_bigger5=0)

    types_animal = await orm_get_types_animal(session)
    btns = {type_animal.animal : str(type_animal.type_animal_id) for type_animal in types_animal}
    await message.answer("Выберите животное", reply_markup=get_callback_btns(btns=btns))
    await state.set_state(AddAnimal.type_animal)

# Хендлер для отлова некорректных вводов для состояния age
@admin_router.message(AddAnimal.age)
async def add_error_age(message: Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные")


# Ловим состояние выбора категории type_animal
@admin_router.callback_query(AddAnimal.type_animal)
async def type_animal(callback: CallbackQuery, state: FSMContext , session: AsyncSession):
    if int(callback.data) in [type_animal.type_animal_id for type_animal in await orm_get_types_animal(session)]:
        await callback.answer()
        await state.update_data(type_animal=callback.data)
        await callback.message.answer('Теперь пол животного', reply_markup=MALE_KB)
        await state.set_state(AddAnimal.male)
    else:
        await callback.message.answer('Выберите катеорию из кнопок.')
        await callback.answer()

# Хендлер для отлова некорректных вводов для состояния type_animal
async def type_animal_error(message: Message, state: FSMContext):
    await message.answer("'Выберите катеорию из кнопок.'")


# Хендлер для отлова ввода для состояния male
@admin_router.message(AddAnimal.male, F.text.in_({'Мужской', 'Женский'}))
async def male(message: Message, state: FSMContext):
    if message.text == "." and AddAnimal.animal_for_change:
        await state.update_data(price=AddAnimal.animal_for_change)
    else:

        await state.update_data(male=message.text)
    await message.answer("Введите медецинскую историю животного", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AddAnimal.medical_history)

# Хендлер для отлова некорректных ввода для состояния male
@admin_router.message(AddAnimal.male)
async def add_price2(message: Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные")


# Ловим состояние выбора категории medical_history
@admin_router.message(AddAnimal.medical_history, F.text)
async def add_med_history(message: Message, state: FSMContext, session: AsyncSession):
    if message.text == "." and AddAnimal.animal_for_change:
        await state.update_data(medical_history=AddAnimal.animal_for_change.medical_history)

    else:
        await state.update_data(medical_history=message.text)
    await message.answer("Введите прививки животного")
    await state.set_state(AddAnimal.vaccinations)


# Хендлер для отлова некорректных ввода для состояния medical_history
@admin_router.message(AddAnimal.medical_history)
async def add_price2(message: Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные")


# Ловим данные для состояние vaccinations и потом выходим из состояний
@admin_router.message(AddAnimal.vaccinations, F.text)
async def add_vacci(message: Message, state: FSMContext, session: AsyncSession):
    if message.text == "." and AddAnimal.animal_for_change:
        await state.update_data(vaccinations=AddAnimal.animal_for_change.vaccinations)
    else:
        await state.update_data(vaccinations=message.text)

    await message.answer("Отлично\nТеперь отправьте фото(при наличнии)", reply_markup=get_keyboard("Нет фото"))
    await state.set_state(AddAnimal.image)


# Ловим все прочее некорректное поведение для этого состояния
@admin_router.message(AddAnimal.vaccinations)
async def add_vaccionation(message: Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные для фото\n"
                        "Если фото нет, то введите 'Нет фото' или нажминте на кнопку")


# Ловим данные для состояние image и потом выходим из состояний
@admin_router.message(AddAnimal.image, or_f(F.photo, F.text == 'Нет фото', F.text == '.'))
async def add_image(message: Message, state: FSMContext, session: AsyncSession):
    if AddAnimal.animal_for_change and message.text == '.':
        await state.update_data(image=AddAnimal.animal_for_change.image)
    elif message.photo:
        await state.update_data(image=message.photo[-1].file_id)
    elif message.text == 'Нет фото':
        await state.update_data(image='None')
    data = await state.get_data()
    print(data)
    try:
        if AddAnimal.animal_for_change:
            await orm_update_animal(session, AddAnimal.animal_for_change.id, data)
        else:
            await orm_add_animal(session, data)
        await message.answer("Животное успешно добавлено", reply_markup=ADMIN_KB)
        await state.clear()

    except Exception as e:
        await message.answer(
            f"Ошибка: \n{str(e)}",
            reply_markup=ADMIN_KB,
        )
        await state.clear()

    AddAnimal.animal_for_change = None

# Ловим все прочее некорректное поведение для этого состояния
@admin_router.message(AddAnimal.image)
async def add_image_error(message: Message, state: FSMContext):
    await message.answer("Отправьте фото животного(при наличии)")
