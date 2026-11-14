import asyncio, logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from db import init_db
from llm import ask_llm

logging.basicConfig(level=logging.INFO)
bot = Bot(token="YOUR_TOKEN")
dp = Dispatcher()
histories: dict[int, list] = {}

@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer("Привет. Задайте вопрос — отвечу по базе знаний.")

@dp.message()
async def handle(m: types.Message):
    uid = m.from_user.id
    hist = histories.setdefault(uid, [])
    answer, need_escalate = await ask_llm(m.text, hist[-10:])
    if need_escalate or not answer:
        await m.answer("Не нашёл точного ответа. Передаю оператору — он скоро напишет.")
        # здесь можно отправить уведомление в админ-чат
        return
    await m.answer(answer)
    hist.append({"role": "user", "content": m.text})
    hist.append({"role": "assistant", "content": answer})

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
