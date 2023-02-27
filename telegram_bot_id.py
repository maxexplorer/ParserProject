from aiogram import Bot, Dispatcher, executor, types
from wildberries_site.config import token

bot = Bot(token=token)

dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def alarm(message: types.Message):
    keyboard_markup = types.InlineKeyboardMarkup()
    user_id_btn = types.InlineKeyboardButton('Получить ID пользывателя из Inline кнопки', callback_data='user_id')
    keyboard_markup.row(user_id_btn)
    await message.answer(f"Ваш ID: {message.from_user.id}", reply_markup=keyboard_markup)


@dp.callback_query_handler(text='user_id')
async def user_id_inline_callback(callback_query: types.CallbackQuery):
    await callback_query.answer(f"Ваш ID: {callback_query.from_user.id}", True)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
