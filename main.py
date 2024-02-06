import asyncio
from aiogram import Dispatcher, types
from createBot import bot
from handlers import user_router, admin_router
from database import create_database

dp = Dispatcher()
dp.include_router(admin_router)
dp.include_router(user_router)


command = types.BotCommand(command='start', description='Запустить бота')

async def main():
    await create_database()
    await bot.set_my_commands(commands=[command])
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    

if __name__ == "__main__":
    asyncio.run(main())