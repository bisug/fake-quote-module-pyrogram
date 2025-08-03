# https://github.com/bisug

from io import BytesIO
from httpx import AsyncClient, Timeout
from contextlib import suppress
import asyncio

from pyrogram import filters
from pyrogram.types import Message
from YOUR APP import app #Replace Your app with your app

fetch = AsyncClient(
    http2=True,
    verify=False,
    headers={
        "Accept-Language": "id-ID",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/107.0.0.0 Safari/537.36 Edge/107.0.1418.42"
        ),
    },
    timeout=Timeout(20),
)


class QuotlyException(Exception):
    ...

async def schedule_deletion(*msgs, delay: int = 300): #autodeletes in 5 minutes 
    await asyncio.sleep(delay)
    for m in msgs:
        with suppress(Exception):
            await m.delete()


async def get_message_sender_id(ctx: Message):
    if ctx.forward_date:
        if ctx.forward_sender_name:
            return 1
        elif ctx.forward_from:
            return ctx.forward_from.id
        elif ctx.forward_from_chat:
            return ctx.forward_from_chat.id
        return 1
    return ctx.from_user.id if ctx.from_user else (
        ctx.sender_chat.id if ctx.sender_chat else 1
    )


async def get_message_sender_name(ctx: Message):
    if ctx.forward_date:
        if ctx.forward_sender_name:
            return ctx.forward_sender_name
        elif ctx.forward_from:
            ln = ctx.forward_from.last_name
            return f"{ctx.forward_from.first_name} {ln}" if ln else ctx.forward_from.first_name
        elif ctx.forward_from_chat:
            return ctx.forward_from_chat.title
        return ""
    if ctx.from_user:
        ln = ctx.from_user.last_name
        return f"{ctx.from_user.first_name} {ln}" if ln else ctx.from_user.first_name
    return ctx.sender_chat.title if ctx.sender_chat else ""


async def get_message_sender_username(ctx: Message):
    if ctx.forward_date:
        if ctx.forward_from_chat and ctx.forward_from_chat.username:
            return ctx.forward_from_chat.username
        return ""
    if ctx.from_user and ctx.from_user.username:
        return ctx.from_user.username
    return (
        ctx.sender_chat.username
        if ctx.sender_chat and ctx.sender_chat.username
        else ""
    )


async def get_message_sender_photo(ctx: Message):
    tgt = None
    if ctx.forward_date:
        if ctx.forward_from and ctx.forward_from.photo:
            tgt = ctx.forward_from.photo
        elif ctx.forward_from_chat and ctx.forward_from_chat.photo:
            tgt = ctx.forward_from_chat.photo
    else:
        if ctx.from_user and ctx.from_user.photo:
            tgt = ctx.from_user.photo
        elif ctx.sender_chat and ctx.sender_chat.photo:
            tgt = ctx.sender_chat.photo
    if not tgt:
        return ""
    return {
        "small_file_id": tgt.small_file_id,
        "small_photo_unique_id": tgt.small_photo_unique_id,
        "big_file_id": tgt.big_file_id,
        "big_photo_unique_id": tgt.big_photo_unique_id,
    }


async def get_text_or_caption(ctx: Message):
    return ctx.text or ctx.caption or ""

async def pyrogram_to_quotly(messages, is_reply: bool):
    if not isinstance(messages, list):
        messages = [messages]

    payload = {
        "type": "quote",
        "format": "png",
        "backgroundColor": "#1b1429",
        "messages": [],
    }

    for msg in messages:
        data = {
            "chatId": await get_message_sender_id(msg),
            "text": await get_text_or_caption(msg),
            "avatar": True,
            "from": {
                "id": await get_message_sender_id(msg),
                "name": await get_message_sender_name(msg),
                "username": await get_message_sender_username(msg),
                "type": msg.chat.type.name.lower(),
                "photo": await get_message_sender_photo(msg),
            },
            "entities": [
                {
                    "type": ent.type.name.lower(),
                    "offset": ent.offset,
                    "length": ent.length,
                }
                for ent in (msg.entities or msg.caption_entities or [])
            ],
            "replyMessage": {},
        }

        if msg.reply_to_message and is_reply:
            rpl = msg.reply_to_message
            data["replyMessage"] = {
                "name": await get_message_sender_name(rpl),
                "text": await get_text_or_caption(rpl),
                "chatId": await get_message_sender_id(rpl),
            }
        payload["messages"].append(data)

    resp = await fetch.post("https://bot.lyo.su/quote/generate.png", json=payload)
    if resp.is_error:
        raise QuotlyException(resp.json())
    return resp.read()

# /fakeq or /fq : Reply-based fake quote (open to all)

@app.on_message(filters.command(["fakeq", "fq"]) & filters.reply)
async def fake_reply_quote(_, ctx: Message):
    if len(ctx.text.split(maxsplit=1)) < 2:
        return await ctx.reply_text(
            "Usage: <code>/fakeq &lt;your text&gt;</code>",
            quote=True,
            parse_mode="HTML",
        )

    fake_text = ctx.text.split(maxsplit=1)[1]
    replied = ctx.reply_to_message

    if not replied.from_user:
        return await ctx.reply_text("Invalid replied user.", quote=True)

    status = await ctx.reply_text("Creating quote...")

    class DummyUser:
        id = replied.from_user.id
        first_name = replied.from_user.first_name or ""
        last_name = replied.from_user.last_name
        username = replied.from_user.username
        emoji_status = type("obj", (), {"custom_emoji_id": None})
        photo = replied.from_user.photo

    class DummyMessage:
        forward_date = None
        forward_sender_name = None
        forward_from = None
        forward_from_chat = None
        from_user = DummyUser()
        sender_chat = None
        chat = type("obj", (), {"type": type("obj", (), {"name": ctx.chat.type.name})})
        text = fake_text
        caption = None
        entities = None
        caption_entities = None
        reply_to_message = None

    try:
        img = await pyrogram_to_quotly([DummyMessage()], is_reply=False)
        file = BytesIO(img)
        file.name = "fake_quote.webp"
        await status.delete()
        sent = await ctx.reply_sticker(file)

        asyncio.create_task(schedule_deletion(ctx, sent))
    except Exception as e:
        await status.delete()
        await ctx.reply_text(f"Error", quote=True)
