import os
import io
from openpyxl import Workbook 
from aiogram import types, Router
from aiogram.filters import CommandStart, Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram import F
from keyboards import builder_admin, builder_inline_admin, builder_inline_user
from createBot import bot
from database import insert_product, delete_product, find_product_by_article, update_product_by_article, create_excel_from_database, search_product_by_article_or_name

ADMIN = [573172666, 853913264, 1313463136]

class Add(StatesGroup):
    photo = State()
    name = State()
    article = State()

class Delete(StatesGroup):
    article = State()

class Edit(StatesGroup):
    article = State()
    prod = State()
    category = State()

admin_router = Router()

@admin_router.message(Command('admin'))
async def check_admin(message: types.Message):
    if message.from_user.id in ADMIN:
        await message.answer(text = 'Вы является администратором бота', reply_markup=builder_admin.as_markup(resize_keyboard=True))

@admin_router.message(F.text == 'Добавить')
async def add(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMIN:
        await state.set_state(Add.photo)
        await state.update_data(photo = [])
        await message.answer(text="Прикрепите фото")

@admin_router.message(Add.photo, F.photo)
#@admin_router.message(F.photo)
async def add_photo(message: types.Message, state: FSMContext):
    #print(message.caption)
    tmp0 = await state.get_data()
    tmp = tmp0['photo']
    tmp.append(message.photo[-1].file_id)
    await state.update_data(photo = tmp)
    # for photo_size in range(0, len(message.photo)):
    #     photo_id = message.photo[photo_size].file_id
    #     photo_file_ids.append(photo_id)
    # print(f"ID присланный фотографии: {photo_file_ids}") 

    # media = []
    # for index, photo_file_id in enumerate(photo_file_ids):
    #     if index == 0:
    #         media.append(types.InputMediaPhoto(media=photo_file_id, caption="Подпись"))
    #     else:
    #         media.append(types.InputMediaPhoto(media=photo_file_id))
    # print(media)
    # # Отправляем группу фотографий
    await state.set_state(Add.name) 
    await message.answer(text="Фото принято. Если хотите загрузить еще одно, то отправьте его. Если фотографий больше не будет, то укажите, какое будет <b>Название товара</b>.", parse_mode="HTML")
    # await bot.send_media_group(chat_id=message.from_user.id, media=media) 
     
    

@admin_router.message(Add.name)
async def add_name(message: types.Message, state: FSMContext):
    await state.update_data(name = message.text)
    await state.set_state(Add.article) 
    await message.answer("Теперь укажите серийный номер")


@admin_router.message(Add.article)
async def add_article(message: types.Message, state: FSMContext):
    prod = await find_product_by_article(message.text)
    if prod == 1:
        await state.update_data(article = message.text)
        await message.answer(text = 'Товар добавлен')
        data = await state.get_data()
        photos = ','.join(data['photo'])
        name = data['name']
        article = data['article']
        await insert_product(photos, name, article)
    else:
        await message.answer(text="Товар с таким серийным номером уже существует")
    await state.clear()

    

@admin_router.message(F.text == 'Удалить')
async def delete(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMIN:
        await message.answer(text = "Введите серийный номер товара, который нужно удалить")
        await state.set_state(Delete.article)

@admin_router.message(Delete.article)
async def delete_article(message: types.Message, state: FSMContext):
    prod = await find_product_by_article(message.text)
    if prod != 1:
        await delete_product(message.text)
        await message.answer("Товар удален")
    else:
        await message.answer(text = "Такого товара нет")
    await state.clear()

@admin_router.message(F.text == 'Изменить')
async def edit(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMIN:
        await message.answer(text = "Введите серийный номер товара, который надо изменить")
        await state.set_state(Edit.article)

@admin_router.message(Edit.article)
async def choice(message: types.Message, state: FSMContext):
    prod = await find_product_by_article(message.text)
    if prod != 1:
        photo_file_ids = prod[1].split(',')
        name = prod[2]
        article = prod[3]
        await state.update_data(prod = prod)
        await state.set_state(Edit.prod)
        media = []
        for index, photo_file_id in enumerate(photo_file_ids):
            if index == 0:
                media.append(types.InputMediaPhoto(media=photo_file_id, caption=f'{name}\nСерийный номер: {article}'))
            else:
                media.append(types.InputMediaPhoto(media=photo_file_id))
            print(media[0])
        await bot.send_media_group(chat_id=message.from_user.id, media=media)
        await message.answer(text="Выберите категорию, которую хотите изменить", reply_markup=builder_inline_admin.as_markup())
    else:
        await message.answer(text="Такого товара нет")
        await state.clear()
tmp = []
@admin_router.callback_query(Edit.prod, F.data == 'photo')
@admin_router.callback_query(Edit.prod, F.data == 'name')
@admin_router.callback_query(Edit.prod, F.data == 'article')
async def new_record(callback: types.CallbackQuery, state: FSMContext):
    global tmp
    tmp = []
    await state.update_data(category = callback.data)
    await state.set_state(Edit.category)
    await callback.message.answer("Введите изменение")


@admin_router.message((Edit.category), ~(F.text == 'Добавить'), ~(F.text == 'Удалить'), ~(F.text == 'Изменить'), ~(F.text == 'Скачать весь товар'), ~(Command('admin')), ~(Command('start')))
async def new_record(message: types.Message, state: FSMContext):
    global tmp
    data = await state.get_data()
    #print(message.content_type)
    category = data['category']
    if category == 'photo' and message.content_type != types.ContentType.TEXT:
        tmp.append(message.photo[-1].file_id)
    else:
        if category == 'name' and message.content_type == types.ContentType.TEXT:
            data['prod'][2] = message.text
        elif category == "article" and message.content_type == types.ContentType.TEXT:
            data['prod'][3] = message.text

    #data = await state.get_data()
    if len(tmp) != 0:
        photos = ','.join(tmp)
    else:
        photos = data['prod'][1]
    name = data['prod'][2]
    article = data['prod'][3]
    await update_product_by_article(data['prod'][0], article, photos, name)
    await message.answer(text="Изменения внесены")
    # tmp = []
    # await state.clear()
    
        

@admin_router.message(F.text == 'Скачать весь товар')
async def create_file(message: types.Message):
    if message.from_user.id in ADMIN:
        workbook = Workbook()
        sheet = workbook.active
        sheet.append(['id', 'photos', 'name', 'article'])
        data = await create_excel_from_database()
        for row in data:
            sheet.append(row)
        # Путь к временному файлу
        temp_file_path = "Your_Excel_File.xlsx"
        # Сохраняем Excel-файл на диск
        workbook.save(temp_file_path)
        doc = FSInputFile(path = "Your_Excel_File.xlsx")
        # Отправляем файл пользователю
        await message.answer_document(doc, caption="Your Excel File.xlsx")
        # Удаляем временный файл после отправки
        os.remove(temp_file_path)


user_router = Router()

@user_router.message(CommandStart())
async def start_cmd(message: types.Message):
    #print(message.from_user.id)
    await message.answer(text="Пришлите название или серийный номер товара для поиска")

@user_router.callback_query(F.data == 'search')
async def check_product(callback: types.CallbackQuery):
    await callback.message.answer(text="Пришлите название или серийный номер товара для поиска")
    


@user_router.message(F.text)
async def check_product(message: types.Message):
    prod = await search_product_by_article_or_name(message.text)
    if prod != 1:
        photo_file_ids = prod[1].split(',')
        name = prod[2]
        article = prod[3]
        media = []
        for index, photo_file_id in enumerate(photo_file_ids):
            if index == 0:
                media.append(types.InputMediaPhoto(media=photo_file_id, caption=f'{name}\nСерийный номер: {article}'))
            else:
                media.append(types.InputMediaPhoto(media=photo_file_id))
        await bot.send_media_group(chat_id=message.from_user.id, media=media)
        await message.answer(text="Выберите действие:", reply_markup=builder_inline_user.as_markup())

    else:
        await message.answer(text="Такого товара нет", reply_markup=builder_inline_user.as_markup())
        

