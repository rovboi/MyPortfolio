import asyncio, logging, os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from telethon import TelegramClient, events
from telethon.sessions import StringSession

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STR = os.getenv("TELETHON_SESSION", "")

# Оба клиента создаются на одном event loop
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
userbot = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)

# ---------- ЮЗЕРБОТ: слушает закрытый канал ----------
@userbot.on(events.NewMessage(chats=["@private_channel_username"]))
async def channel_listener(event):
    text = event.message.message or ""
    if "срочно" in text.lower() or "важно" in text.lower():
        # Пересылаем владельцу в бот через того же бота
        await bot.send_message(
            chat_id=os.getenv("OWNER_ID"),
            text=f"🔔 Сигнал из канала:\n\n{text[:500]}"
        )

# ---------- БОТ: интерфейс ----------
@dp.message(Command("start"))
async def start(m: types.Message):
    me = await userbot.get_me()
    await m.answer(
        f"Гибридный бот запущен.\n"
        f"Юзербот: @{me.username}\n"
        f"Слушаю канал и пересылаю важное."
    )

# ---------- ОДИН EVENT LOOP ----------
async def main():
    await userbot.start()
    print("Userbot connected")
    # Запускаем polling aiogram и держим userbot живым в одном gather
    await asyncio.gather(
        dp.start_polling(bot),
        userbot.run_until_disconnected()
    )

if __name__ == "__main__":
    asyncio.run(main())
