import aiohttp, os

TONCENTER = "https://toncenter.com/api/v2"
API_KEY = os.getenv("TONCENTER_API_KEY", "")
MY_WALLET = os.getenv("MY_TON_WALLET", "").strip()

async def find_payment(tx_comment: str, min_nanotons: int = 100_000_000) -> dict | None:
    """Ищет входящий перевод на MY_WALLET с нужным комментарием."""
    url = f"{TONCENTER}/getTransactions"
    params = {"address": MY_WALLET, "limit": 50, "api_key": API_KEY}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            data = await resp.json()
    for tx in data.get("result", []):
        in_msg = tx.get("in_msg", {})
        if in_msg.get("source") == MY_WALLET:
            continue
        value = int(in_msg.get("value", 0))
        comment = in_msg.get("message", "")
        if comment == tx_comment and value >= min_nanotons:
            return {"tx_hash": tx.get("transaction_id", {}).get("hash"),
                    "value": value, "comment": comment}
    return None
