from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

builder_admin = ReplyKeyboardBuilder()
builder_admin.button(text="Добавить")
builder_admin.button(text="Удалить")
builder_admin.button(text="Изменить")
builder_admin.button(text="Скачать весь товар")
builder_admin.adjust(2,2)

builder_inline_admin = InlineKeyboardBuilder()
builder_inline_admin.button(text="Фото", callback_data='photo')
builder_inline_admin.button(text="Название", callback_data='name')
builder_inline_admin.button(text="Серийный номер", callback_data='article')
builder_inline_admin.adjust(1,1,1)

builder_inline_user = InlineKeyboardBuilder()
builder_inline_user.button(text="Поиск товара", callback_data='search')
builder_inline_user.button(text="Связь с администратором", url="t.me/mef_rk")