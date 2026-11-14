import json
from openai import AsyncOpenAI
from db import search_kb

client = AsyncOpenAI()

TOOLS = [{
    "type": "function",
    "function": {
        "name": "search_kb",
        "description": "Ищет ответ в базе знаний. Вызывай ВСЕГДА перед ответом.",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"]
        }
    }
}]

async def ask_llm(user_text: str, history: list[dict]) -> tuple[str, bool]:
    messages = [
        {"role": "system", "content": (
            "Ты ассистент поддержки. Отвечай ТОЛЬКО по данным из search_kb. "
            "Если в базе нет ответа — верни маркер [ESCALATE]."
        )},
        *history,
        {"role": "user", "content": user_text}
    ]
    resp = await client.chat.completions.create(
        model="gpt-4o-mini", messages=messages, tools=TOOLS, tool_choice="auto"
    )
    msg = resp.choices[0].message
    if msg.tool_calls:
        results = []
        for tc in msg.tool_calls:
            if tc.function.name == "search_kb":
                args = json.loads(tc.function.arguments)
                results.extend(await search_kb(args["query"]))
        messages.append(msg)
        messages.append({
            "role": "tool",
            "tool_call_id": msg.tool_calls[0].id,
            "content": json.dumps(results, ensure_ascii=False)
        })
        final = await client.chat.completions.create(
            model="gpt-4o-mini", messages=messages
        )
        answer = final.choices[0].message.content or ""
        return answer.replace("[ESCALATE]", "").strip(), "[ESCALATE]" in answer
    return msg.content or "", True  # модель не вызвала поиск → эскалация
