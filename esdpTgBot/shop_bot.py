import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
import httpx
from aiogram.types import URLInputFile, WebAppInfo


async def shop_data():
    async with httpx.AsyncClient() as client:
        response = await client.get('http://django-app:8000/api/shop_for_telegram/')
        result = response.json()

        return result


class ShopBot:
    def __init__(self, token, shop_data):
        self.token = token
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.shop_data = shop_data

        @self.dp.message(Command('start'))
        async def start(message: types.Message):
            try:
                image_from_url = URLInputFile(self.shop_data['logo'])
                await message.answer_photo(image_from_url,
                                       caption=f'Здраствуйте! Вас приветствует бот магазина: {self.shop_data["name"]}\n'
                                               f'Описание нашего магазина: {self.shop_data["description"]}'
                                               )

            except Exception as e:
                print(e)

        @self.dp.message(Command('info'))
        async def info(message: types.Message):
            buttons = [
                [
                    types.InlineKeyboardButton(text="Оформить досатвку", callback_data='test2'),
                    types.InlineKeyboardButton(text="Каталог магазина ", web_app=WebAppInfo(
                        url=f"https://market.shopuchet.kz/shop/{self.shop_data['id']}"))
                ],
                [types.InlineKeyboardButton(text="Перейти на наш сайт", url=f'https://market.shopuchet.kz/shop/{self.shop_data["id"]}')]
            ]
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

            await message.answer(
                'Что я могу:',
                reply_markup=keyboard
            )

    async def run(self):
        await self.dp.start_polling(self.bot)


async def main() -> None:
        shop_data_list = await shop_data()
        bots = [ShopBot(token=shop['tg_token'], shop_data=shop) for shop in shop_data_list]
        await asyncio.gather(*(bot.run() for bot in bots))



if __name__ == '__main__':
    asyncio.run(main())
