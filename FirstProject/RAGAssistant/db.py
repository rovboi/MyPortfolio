import aiosqlite
from pathlib import Path

DB_PATH = Path("support.db")

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS kb_fts USING fts5(
                title, content, tokenize='porter unicode61'
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS dialogues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER, user_msg TEXT, bot_msg TEXT,
                escalated INTEGER DEFAULT 0,
                ts DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

async def search_kb(query: str, limit: int = 3) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT title, content, rank FROM kb_fts
            WHERE kb_fts MATCH ? ORDER BY rank LIMIT ?
        """, (query, limit))
        rows = await cursor.fetchall()
        return [{"title": r[0], "content": r[1], "rank": r[2]} for r in rows]
