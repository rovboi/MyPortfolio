import asyncio, uuid, logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ton_checker import find_payment

logging.basicConfig(level=logging.INFO)
bot = Bot(token="YOUR_TOKEN")
dp = Dispatcher()

PRODUCTS = {"pro": {"name": "PRO доступ", "price_ton": 1},
            "vip": {"name": "VIP доступ", "price_ton": 3}}

pending: dict[int, dict] = {}

@dp.message(Command("start"))
async def start(m: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="PRO (1 TON)", callback_data="buy:pro")],
        [InlineKeyboardButton(text="VIP (3 TON)", callback_data="buy:vip")],
    ])
    await m.answer("Выберите товар:", reply_markup=kb)

@dp.callback_query(lambda c: c.data.startswith("buy:"))
async def buy(cb: types.CallbackQuery):
    sku = cb.data.split(":")[1]
    product = PRODUCTS[sku]
    comment = f"ORDER-{uuid.uuid4().hex[:10]}"
    pending[cb.from_user.id] = {"sku": sku, "comment": comment}
    await cb.message.edit_text(
        f"Переведите *{product['price_ton']} TON* на кошелёк:\n`{os.getenv('MY_TON_WALLET')}`\n\n"
        f"Комментарий: `{comment}`\n\nПосле оплаты нажмите «Я оплатил».",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Я оплатил ✅", callback_data="check")]
        ])
    )
    await cb.answer()

@dp.callback_query(lambda c: c.data == "check")
async def check(cb: types.CallbackQuery):
    data = pending.get(cb.from_user.id)
    if not data:
        await cb.answer("Сначала выберите товар.", show_alert=True); return
    payment = await find_payment(data["comment"])
    if payment:
        # Здесь — выдача доступа: запись в БД, отправка файла и т.д.
        await cb.message.edit_text(
            f"✅ Оплата подтверждена! Хеш: `{payment['tx_hash'][:16]}...`\n"
            f"Доступ «{PRODUCTS[data['sku']]['name']}» активирован."
        )
        pending.pop(cb.from_user.id, None)
    else:
        await cb.answer("Платёж не найден. Подождите 30 сек и проверьте снова.", show_alert=True)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
