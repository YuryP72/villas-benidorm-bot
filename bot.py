import os, json, logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, FSInputFile
from typing import Dict

logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

# --- REAL DATA FROM YOUR SITE - NO CREATIVE ---
VILLA = {
    "id": "residence",
    "main": "https://villas-benidorm.com/renders/residence.jpg",
    "gallery": [
        "https://villas-benidorm.com/renders/residence.jpg",
        "https://villas-benidorm.com/renders/modern_villa_sunset.jpg",
        "https://villas-benidorm.com/renders/modern_villa_forest_reflection.jpg",
        "https://villas-benidorm.com/renders/modern_villa_pool_after_dark.jpg",
        "https://villas-benidorm.com/renders/golden_evening_living_room.jpg",
    ],
    "plans": {
        "basement": {"url": "https://villas-benidorm.com/renders/plans/floor-1.png", "name": "Basement -1 / Sótano"},
        "ground": {"url": "https://villas-benidorm.com/renders/plans/floor0.png", "name": "Ground Floor / Planta Baja"},
        "first": {"url": "https://villas-benidorm.com/renders/plans/floor1.png", "name": "First Floor / Planta Primera"},
    }
}

SESSIONS: Dict[int, dict] = {}

TEXTS = {
    "ru": {"new_lead": "🔥 Новый лид с villas-benidorm.com", "reply_hint": "Ответь Reply чтобы написать клиенту на сайт"},
    "en": {"new_lead": "🔥 New lead from villas-benidorm.com", "reply_hint": "Reply to message to answer client"},
    "es": {"new_lead": "🔥 Nuevo lead", "reply_hint": "Responde para escribir al cliente"}
}

async def notify_admin(lead: dict):
    lang = lead.get("lang", "ru")
    t = TEXTS.get("ru")
    text = (
        f"{t['new_lead']}\n\n"
        f"🏡 Villa: {lead.get('villa_id','residence')}\n"
        f"🌐 Lang: {lead.get('lang')} | {lead.get('page_url','')}\n"
        f"👤 {lead.get('name')} | 📞 {lead.get('phone')} | 📧 {lead.get('email')}\n\n"
        f"💬 {lead.get('message')}\n\n"
        f"ID: {lead.get('session_id')}\n_{t['reply_hint']}_"
    )
    # кнопки с реальными планировками
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗺️ Basement -1", url=VILLA["plans"]["basement"]["url"]),
         InlineKeyboardButton(text="🗺️ Ground", url=VILLA["plans"]["ground"]["url"])],
        [InlineKeyboardButton(text="🗺️ First Floor", url=VILLA["plans"]["first"]["url"])],
        [InlineKeyboardButton(text="🖼️ Все рендеры", callback_data="send_gallery")]
    ])
    admin_id = os.getenv("ADMIN_CHAT_ID")
    msg = await bot.send_message(chat_id=admin_id, text=text, reply_markup=kb, parse_mode="Markdown")
    SESSIONS[msg.message_id] = lead
    SESSIONS[lead.get('session_id')] = lead
    return msg.message_id

@dp.message(Command("start", "villa"))
async def cmd_villa(m: types.Message):
    # Отправляем реальную галерею с сайта
    media = []
    for i, url in enumerate(VILLA["gallery"][:5]):
        caption = f"Residence - {i+1}/5\n{villa_url_note()}" if i==0 else None
        media.append(InputMediaPhoto(media=url, caption=caption))
    await m.answer_media_group(media=media)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📍 Локация", url="https://villas-benidorm.com/#location"),
         InlineKeyboardButton(text="🗺️ Планировки", callback_data="plans")],
        [InlineKeyboardButton(text="💶 Цены", url="https://villas-benidorm.com/#price"),
         InlineKeyboardButton(text="📅 Записаться на просмотр", callback_data="book")],
    ])
    await m.answer("Выбери раздел — все данные с villas-benidorm.com", reply_markup=kb)

def villa_url_note():
    return "Фото: villas-benidorm.com/renders/"

@dp.callback_query(F.data == "plans")
async def cb_plans(cb: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Basement -1", url=VILLA["plans"]["basement"]["url"])],
        [InlineKeyboardButton(text="Ground Floor", url=VILLA["plans"]["ground"]["url"])],
        [InlineKeyboardButton(text="First Floor", url=VILLA["plans"]["first"]["url"])],
    ])
    await cb.message.answer(f"Планировки с сайта:\nBasement: floor-1.png\nGround: floor0.png\nFirst: floor1.png", reply_markup=kb)
    await cb.answer()

@dp.callback_query(F.data == "send_gallery")
async def cb_gallery(cb: types.CallbackQuery):
    media = [InputMediaPhoto(media=u) for u in VILLA["gallery"]]
    await cb.message.answer_media_group(media=media)
    await cb.answer()

@dp.message(F.reply_to_message)
async def handle_reply(m: types.Message):
    replied_id = m.reply_to_message.message_id
    lead = SESSIONS.get(replied_id)
    if not lead:
        await m.answer("Сессия не найдена, бот перезапускался на Render free.")
        return
    import pathlib, json
    session_id = lead.get('session_id')
    path = pathlib.Path(f"/tmp/villas_chats/{session_id}.json")
    history = []
    if path.exists():
        try: history = json.loads(path.read_text(encoding='utf-8'))
        except: pass
    history.append({"from_admin": True, "text": m.text or m.caption or "", "timestamp": m.date.isoformat()})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(history, ensure_ascii=False), encoding='utf-8')
    await m.answer("✅ Отправлено клиенту на сайт")

async def handle_webhook_update(update_dict: dict):
    update = types.Update.model_validate(update_dict)
    await dp.feed_update(bot, update)
