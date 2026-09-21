
import os, json, logging, pathlib
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from typing import Dict

logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

# --- EXACT PRICES FROM villas-benidorm.com SCREENSHOT ---
VILLAS = {
    "villa01": {
        "id": "villa01",
        "name": {"en": "VILLA 01", "es": "VILLA 01", "ru": "VILLA 01"},
        "full_name": {"en": "VILLA 01 — Premium", "es": "VILLA 01 — Premium", "ru": "VILLA 01 — Premium"},
        "built": "470 M²",
        "beds": "5 BED",
        "beds_detail": {"en": "5 Bedrooms / 5 Bathrooms", "es": "5 Dormitorios / 5 Baños", "ru": "5 Спален / 5 Ванных"},
        "price": "€2,725,000",
        "main": "https://villas-benidorm.com/renders/residence.jpg",
        "gallery": [
            "https://villas-benidorm.com/renders/residence.jpg",
            "https://villas-benidorm.com/renders/modern_villa_sunset.jpg",
            "https://villas-benidorm.com/renders/modern_villa_forest_reflection.jpg",
            "https://villas-benidorm.com/renders/modern_villa_pool_after_dark.jpg",
            "https://villas-benidorm.com/renders/golden_evening_living_room.jpg",
        ],
        "plans": {
            "basement": "https://villas-benidorm.com/renders/plans/floor-1.png",
            "ground": "https://villas-benidorm.com/renders/plans/floor0.png",
            "first": "https://villas-benidorm.com/renders/plans/floor1.png",
        },
        "delivery": "2027"
    },
    "villa02": {
        "id": "villa02",
        "name": {"en": "VILLA 02", "es": "VILLA 02", "ru": "VILLA 02"},
        "full_name": {"en": "VILLA 02 — Premium", "es": "VILLA 02 — Premium", "ru": "VILLA 02 — Premium"},
        "built": "470 M²",
        "beds": "5 BED",
        "beds_detail": {"en": "5 Bedrooms / 5 Bathrooms", "es": "5 Dormitorios / 5 Baños", "ru": "5 Спален / 5 Ванных"},
        "price": "€2,885,000",
        "main": "https://villas-benidorm.com/renders/modern_villa_sunset.jpg",
        "gallery": [
            "https://villas-benidorm.com/renders/modern_villa_sunset.jpg",
            "https://villas-benidorm.com/renders/modern_villa_forest_reflection.jpg",
            "https://villas-benidorm.com/renders/modern_villa_pool_after_dark.jpg",
            "https://villas-benidorm.com/renders/golden_evening_living_room.jpg",
            "https://villas-benidorm.com/renders/residence.jpg",
        ],
        "plans": {
            "basement": "https://villas-benidorm.com/renders/plans/floor-1.png",
            "ground": "https://villas-benidorm.com/renders/plans/floor0.png",
            "first": "https://villas-benidorm.com/renders/plans/floor1.png",
        },
        "delivery": "2027"
    },
    "villa03": {
        "id": "villa03",
        "name": {"en": "VILLA 03", "es": "VILLA 03", "ru": "VILLA 03"},
        "full_name": {"en": "VILLA 03 — Premium", "es": "VILLA 03 — Premium", "ru": "VILLA 03 — Premium"},
        "built": "470 M²",
        "beds": "5 BED",
        "beds_detail": {"en": "5 Bedrooms / 5 Bathrooms", "es": "5 Dormitorios / 5 Baños", "ru": "5 Спален / 5 Ванных"},
        "price": "€2,835,000",
        "main": "https://villas-benidorm.com/renders/modern_villa_forest_reflection.jpg",
        "gallery": [
            "https://villas-benidorm.com/renders/modern_villa_forest_reflection.jpg",
            "https://villas-benidorm.com/renders/modern_villa_pool_after_dark.jpg",
            "https://villas-benidorm.com/renders/golden_evening_living_room.jpg",
            "https://villas-benidorm.com/renders/residence.jpg",
            "https://villas-benidorm.com/renders/modern_villa_sunset.jpg",
        ],
        "plans": {
            "basement": "https://villas-benidorm.com/renders/plans/floor-1.png",
            "ground": "https://villas-benidorm.com/renders/plans/floor0.png",
            "first": "https://villas-benidorm.com/renders/plans/floor1.png",
        },
        "delivery": "2027"
    }
}

VILLA = VILLAS["villa01"]
SESSIONS: Dict[int, dict] = {}
USER_LANG: Dict[int, str] = {}
USER_VILLA: Dict[int, str] = {}

class BookingForm(StatesGroup):
    name = State()
    phone = State()
    date = State()
    comment = State()

TEXTS = {
    "en": {
        "welcome_gallery_caption": "Villas Benidorm — 3 Premium Villas",
        "welcome_title": "💎 Villas Benidorm — villas-benidorm.com\n\n3 exclusive modern villas — 470 M² • 5 BED each.\nPrices as on website.",
        "choose_lang": "Please choose your language / Elige tu idioma / Выберите язык:",
        "lang_en": "🇬🇧 English", "lang_es": "🇪🇸 Español", "lang_ru": "🇷🇺 Русский",
        "lang_set": "Language: English 🇬🇧",
        "choose_villa": "🏡 *Choose your villa — prices as on villas-benidorm.com:*\n\nVILLA 01 — €2,725,000 — 470 M² • 5 BED\nVILLA 02 — €2,885,000 — 470 M² • 5 BED\nVILLA 03 — €2,835,000 — 470 M² • 5 BED\n\nDelivery: 2027",
        "main_menu": "🏡 *{villa_name} — {price}*\n470 M² • 5 BED • Delivery 2027\n\nWhat would you like to explore?",
        "btn_price": "💶 Price & Details", "btn_location": "📍 Location", "btn_plans": "🗺️ Floor Plans",
        "btn_gallery": "🖼️ Gallery", "btn_book": "📅 Book Viewing", "btn_lang": "🌐 Language", "btn_villas": "🏘️ All 3 Villas",
        "price_title": "💶 *{villa_name} — {price}*",
        "price_text": " *{villa_name}*\nPrice: *{price}* — as on villas-benidorm.com\n\n• Built: {built} • {beds_detail}\n• Plot: sea view, infinity pool 14m, jacuzzi\n• Grenton Smart Home, underfloor heating\n• A+ energy, triple-glazed aluminium\n• Panoramic windows, 2 parkings\n• 3 levels: Basement -1, Ground, First\n\nDelivery: *{delivery}*\nNo VAT mention — price as on website.",
        "location_title": "📍 *Location — villas-benidorm.com*", "location_text": " *Finestrat — Benidorm, Costa Blanca*\nPrivileged hilltop, panoramic Mediterranean & skyline.\n\n• 1.2 km to Levante Beach\n• 3 min to Finestrat center\n• 5 min to Terra Mítica\n• 45 min to Alicante Airport\n\nQuiet residential Las Villas, SE orientation, all-day sun. Delivery 2027.",
        "plans_title": "🗺️ *{villa_name} — Plans 470 M²*", "plans_text": "Floor plans from villas-benidorm.com displayed directly:",
        "gallery_title": "🖼️ *{villa_name} — Gallery*", "book_title": "📅 *Book Viewing — {villa_name}*",
        "book_start": "Viewing for *{villa_name}* — {price}\n\nYour full name?", "book_phone": "Thanks {name}!\n\nPhone / WhatsApp with country code:",
        "book_date": "Preferred date & time? (e.g. Sep 25, 17:00)", "book_comment": "Any preferences? (language EN/ES/RU, budget...)",
        "book_confirm_user": "✅ Thank you {name}!\n\nRequest for *{villa_name}* ({price}) — 470 M² • 5 BED\n• Date: {date}\n• Phone: {phone}\n\nManager will contact in 30 min. Delivery 2027.",
        "book_admin": "🔥 *NEW BOOKING*", "new_lead": "🔥 New lead", "reply_hint": "Reply to answer client", "back": "⬅️ Back", "menu_hint": "Choose:", "villas_list": "🏘️ 3 Villas from villas-benidorm.com — prices as on site:"
    },
    "es": {
        "welcome_gallery_caption": "Villas Benidorm — 3 Villas Premium",
        "welcome_title": "💎 Villas Benidorm — villas-benidorm.com\n\n3 villas modernas exclusivas — 470 M² • 5 DORM cada una.\nPrecios como en la web.",
        "choose_lang": "Elige tu idioma:", "lang_en": "🇬🇧 English", "lang_es": "🇪🇸 Español", "lang_ru": "🇷🇺 Русский",
        "lang_set": "Idioma: Español 🇪🇸",
        "choose_villa": "🏡 *Elige tu villa — precios como en villas-benidorm.com:*\n\nVILLA 01 — €2,725,000 — 470 M² • 5 DORM\nVILLA 02 — €2,885,000 — 470 M² • 5 DORM\nVILLA 03 — €2,835,000 — 470 M² • 5 DORM\n\nEntrega: 2027",
        "main_menu": "🏡 *{villa_name} — {price}*\n470 M² • 5 DORM • Entrega 2027\n\n¿Qué quieres explorar?",
        "btn_price": "💶 Precio y Detalles", "btn_location": "📍 Ubicación", "btn_plans": "🗺️ Planos", "btn_gallery": "🖼️ Galería", "btn_book": "📅 Reservar Visita", "btn_lang": "🌐 Idioma", "btn_villas": "🏘️ Las 3 Villas",
        "price_title": "💶 *{villa_name} — {price}*", "price_text": " *{villa_name}*\nPrecio: *{price}* — como en villas-benidorm.com\n\n• Construida: {built} • {beds_detail}\n• Parcela: vista al mar, piscina infinita 14m, jacuzzi\n• Casa inteligente Grenton, suelo radiante\n• Energía A+, triple vidrio\n• Ventanales panorámicos, 2 parkings\n• 3 plantas: Sótano -1, Baja, Primera\n\nEntrega: *{delivery}*",
        "location_title": "📍 *Ubicación*", "location_text": " *Finestrat — Benidorm, Costa Blanca*\nEn colina con vistas panorámicas.\n\n• 1,2 km a Playa Levante\n• 3 min a centro Finestrat\n• 5 min a Terra Mítica\n• 45 min a Aeropuerto Alicante\n\nResidencial Las Villas, SE, sol todo el día. Entrega 2027.",
        "plans_title": "🗺️ *{villa_name} — Planos 470 M²*", "plans_text": "Planos de villas-benidorm.com directos:", "gallery_title": "🖼️ *{villa_name} — Galería*", "book_title": "📅 *Reservar Visita — {villa_name}*",
        "book_start": "Visita para *{villa_name}* — {price}\n\n¿Nombre completo?", "book_phone": "Gracias {name}!\n\nTeléfono / WhatsApp:", "book_date": "¿Fecha y hora preferida?", "book_comment": "¿Preferencias? (idioma ES/EN/RU...)",
        "book_confirm_user": "✅ ¡Gracias {name}!\n\nSolicitud para *{villa_name}* ({price}) — 470 M² • 5 DORM\n• Fecha: {date}\n• Tel: {phone}\n\nGestor contactará en 30 min. Entrega 2027.",
        "book_admin": "🔥 *NUEVA RESERVA*", "new_lead": "🔥 Nuevo lead", "reply_hint": "Responde para contestar", "back": "⬅️ Volver", "menu_hint": "Elige:", "villas_list": "🏘️ 3 Villas de villas-benidorm.com — precios como en la web:"
    },
    "ru": {
        "welcome_gallery_caption": "Villas Benidorm — 3 премиальные виллы",
        "welcome_title": "💎 Villas Benidorm — villas-benidorm.com\n\n3 эксклюзивные современные виллы — 470 M² • 5 спален каждая.\nЦены как на сайте.",
        "choose_lang": "Выберите язык:", "lang_en": "🇬🇧 English", "lang_es": "🇪🇸 Español", "lang_ru": "🇷🇺 Русский",
        "lang_set": "Язык: Русский 🇷🇺",
        "choose_villa": "🏡 *Выберите виллу — цены как на villas-benidorm.com:*\n\nVILLA 01 — €2,725,000 — 470 M² • 5 BED\nVILLA 02 — €2,885,000 — 470 M² • 5 BED\nVILLA 03 — €2,835,000 — 470 M² • 5 BED\n\nСдача: 2027",
        "main_menu": "🏡 *{villa_name} — {price}*\n470 M² • 5 BED • Сдача 2027\n\nЧто хотите узнать?",
        "btn_price": "💶 Цена и характеристики", "btn_location": "📍 Расположение", "btn_plans": "🗺️ Планировки", "btn_gallery": "🖼️ Галерея", "btn_book": "📅 Запись на просмотр", "btn_lang": "🌐 Язык", "btn_villas": "🏘️ Все 3 виллы",
        "price_title": "💶 *{villa_name} — {price}*", "price_text": " *{villa_name}*\nЦена: *{price}* — как на villas-benidorm.com\n\n• Построено: {built} • {beds_detail}\n• Участок: вид на море, бассейн инфинити 14м, джакузи\n• Умный дом Grenton, теплый пол\n• Энерго A+, тройной стеклопакет\n• Панорамные окна, 2 паркинга\n• 3 уровня: Цоколь -1, 1 этаж, 2 этаж\n\nСдача: *{delivery}*",
        "location_title": "📍 *Расположение*", "location_text": " *Финестрат — Бенидорм, Коста-Бланка*\nНа холме с панорамным видом на море и skyline.\n\n• 1,2 км до пляжа Леванте\n• 3 мин до центра Финестрат\n• 5 мин до Terra Mítica\n• 45 мин до аэропорта Аликанте\n\nКомплекс Las Villas, ЮВ, солнце весь день. Сдача 2027.",
        "plans_title": "🗺️ *{villa_name} — Планировки 470 M²*", "plans_text": "Планировки с villas-benidorm.com напрямую:", "gallery_title": "🖼️ *{villa_name} — Галерея*", "book_title": "📅 *Запись — {villa_name}*",
        "book_start": "Запись на *{villa_name}* — {price}\n\nКак вас зовут?", "book_phone": "Спасибо {name}!\n\nТелефон / WhatsApp с кодом страны:", "book_date": "Удобная дата и время?", "book_comment": "Пожелания? (язык RU/EN/ES, бюджет...)",
        "book_confirm_user": "✅ Спасибо {name}!\n\nЗаявка на *{villa_name}* ({price}) — 470 M² • 5 BED\n• Дата: {date}\n• Телефон: {phone}\n\nМенеджер свяжется за 30 мин. Сдача 2027.",
        "book_admin": "🔥 *НОВАЯ ЗАПИСЬ*", "new_lead": "🔥 Новый лид", "reply_hint": "Ответь Reply чтобы написать клиенту", "back": "⬅️ Назад", "menu_hint": "Выберите:", "villas_list": "🏘️ 3 виллы с villas-benidorm.com — цены как на сайте:"
    }
}

def get_lang(uid: int) -> str:
    return USER_LANG.get(uid, "en")

def get_villa(uid: int) -> str:
    return USER_VILLA.get(uid, "villa01")

def lang_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton(text="🇪🇸 Español", callback_data="lang_es")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
    ])

def villas_kb(lang: str):
    rows = []
    for vid in ["villa01", "villa02", "villa03"]:
        v = VILLAS[vid]
        rows.append([InlineKeyboardButton(text=f"{v['name'][lang]} — {v['price']} — {v['built']} • {v['beds']}", callback_data=f"villa_{vid}")])
    rows.append([InlineKeyboardButton(text=TEXTS[lang]["btn_lang"], callback_data="change_lang")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def main_menu_kb(lang: str, villa_id: str):
    t = TEXTS[lang]
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t["btn_price"], callback_data=f"price_{villa_id}"),
         InlineKeyboardButton(text=t["btn_location"], callback_data=f"loc_{villa_id}")],
        [InlineKeyboardButton(text=t["btn_plans"], callback_data=f"plans_{villa_id}"),
         InlineKeyboardButton(text=t["btn_gallery"], callback_data=f"gallery_{villa_id}")],
        [InlineKeyboardButton(text=t["btn_book"], callback_data=f"book_{villa_id}")],
        [InlineKeyboardButton(text=t["btn_villas"], callback_data="all_villas"),
         InlineKeyboardButton(text=t["btn_lang"], callback_data="change_lang")],
    ])

def back_to_villa_kb(lang: str, villa_id: str):
    t = TEXTS[lang]
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t["back"], callback_data=f"villa_{villa_id}")]])

async def notify_admin(lead: dict):
    lang = lead.get("lang", "en")
    t = TEXTS.get(lang, TEXTS["en"])
    villa_id = lead.get("villa_id", "villa01")
    v = VILLAS.get(villa_id, VILLAS["villa01"])
    is_booking = "booking_date" in lead and lead.get("booking_date")
    if is_booking:
        text = f"{t['book_admin']} {v['name'][lang]} — {v['price']}\n\n🏡 Villa: {villa_id} | {v['price']} | {v['built']} {v['beds']}\n🌐 Lang: {lead.get('lang')} | {lead.get('page_url','bot')}\n👤 {lead.get('name')} | 📞 {lead.get('phone')}\n📅 Date: {lead.get('booking_date')}\n💬 {lead.get('message')}\n\nID: {lead.get('session_id')}\n_{t['reply_hint']}_"
    else:
        text = f"{t['new_lead']} {v['name'][lang]} {v['price']}\n\n🏡 {villa_id} {v['price']} {v['built']}\n🌐 Lang: {lead.get('lang')}\n👤 {lead.get('name')} | 📞 {lead.get('phone')}\n💬 {lead.get('message')}\n\nID: {lead.get('session_id')}\n_{t['reply_hint']}_"
    admin_id = os.getenv("ADMIN_CHAT_ID")
    if not admin_id:
        return None
    try:
        msg = await bot.send_message(chat_id=admin_id, text=text, parse_mode="Markdown")
        SESSIONS[msg.message_id] = lead
        SESSIONS[lead.get('session_id')] = lead
        return msg.message_id
    except Exception as e:
        logging.error(f"notify_admin {e}")
        return None

@dp.message(Command("start", "villa", "lang"))
async def cmd_start(m: types.Message, state: FSMContext):
    await state.clear()
    uid = m.from_user.id
    default_lang = USER_LANG.get(uid, "en")
    try:
        media = [InputMediaPhoto(media=VILLAS["villa01"]["gallery"][i], caption=TEXTS[default_lang]["welcome_gallery_caption"] if i==0 else None) for i in range(3)]
        await m.answer_media_group(media=media)
    except Exception as e:
        logging.error(e)
        await m.answer_photo(photo=VILLAS["villa01"]["main"], caption=TEXTS[default_lang]["welcome_gallery_caption"])
    t = TEXTS[default_lang]
    await m.answer(f"{t['welcome_title']}\n\n{t['choose_lang']}", reply_markup=lang_kb())

@dp.callback_query(F.data.startswith("lang_"))
async def cb_set_lang(cb: types.CallbackQuery):
    lang = cb.data.split("_")[1]
    if lang not in TEXTS: lang="en"
    USER_LANG[cb.from_user.id] = lang
    t = TEXTS[lang]
    await cb.answer(t["lang_set"])
    await cb.message.answer(t["choose_villa"], reply_markup=villas_kb(lang), parse_mode="Markdown")

@dp.callback_query(F.data == "change_lang")
async def cb_change_lang(cb: types.CallbackQuery):
    lang = get_lang(cb.from_user.id)
    t = TEXTS[lang]
    await cb.message.answer(t["choose_lang"], reply_markup=lang_kb())
    await cb.answer()

@dp.callback_query(F.data == "all_villas")
async def cb_all_villas(cb: types.CallbackQuery):
    lang = get_lang(cb.from_user.id)
    t = TEXTS[lang]
    await cb.message.answer(t["villas_list"] + "\n\n" + t["choose_villa"], reply_markup=villas_kb(lang), parse_mode="Markdown")
    await cb.answer()

@dp.callback_query(F.data.startswith("villa_"))
async def cb_villa(cb: types.CallbackQuery):
    villa_id = cb.data.split("_")[1]
    if villa_id not in VILLAS: villa_id="villa01"
    USER_VILLA[cb.from_user.id]=villa_id
    lang = get_lang(cb.from_user.id)
    v = VILLAS[villa_id]
    t = TEXTS[lang]
    await cb.message.answer(t["main_menu"].format(villa_name=v["name"][lang], price=v["price"]), reply_markup=main_menu_kb(lang, villa_id), parse_mode="Markdown")
    await cb.answer()

@dp.callback_query(F.data.startswith("price_"))
async def cb_price(cb: types.CallbackQuery):
    villa_id = cb.data.split("_")[1]
    if villa_id not in VILLAS: villa_id=get_villa(cb.from_user.id)
    lang = get_lang(cb.from_user.id)
    v = VILLAS[villa_id]
    t = TEXTS[lang]
    text = t["price_text"].format(villa_name=v["name"][lang], price=v["price"], built=v["built"], beds_detail=v["beds_detail"][lang], delivery=v["delivery"])
    await cb.message.answer(f"{t['price_title'].format(villa_name=v['name'][lang])}\n\n{text}", reply_markup=back_to_villa_kb(lang, villa_id), parse_mode="Markdown")
    await cb.answer()

@dp.callback_query(F.data.startswith("loc_"))
async def cb_loc(cb: types.CallbackQuery):
    villa_id = cb.data.split("_")[1]
    if villa_id not in VILLAS: villa_id=get_villa(cb.from_user.id)
    lang = get_lang(cb.from_user.id)
    t = TEXTS[lang]
    await cb.message.answer(f"{t['location_title']}\n\n{t['location_text']}", reply_markup=back_to_villa_kb(lang, villa_id), parse_mode="Markdown")
    await cb.answer()

@dp.callback_query(F.data.startswith("plans_"))
async def cb_plans(cb: types.CallbackQuery):
    villa_id = cb.data.split("_")[1]
    if villa_id not in VILLAS: villa_id=get_villa(cb.from_user.id)
    lang = get_lang(cb.from_user.id)
    v = VILLAS[villa_id]
    t = TEXTS[lang]
    await cb.message.answer(f"{t['plans_title'].format(villa_name=v['name'][lang])}\n\n{t['plans_text']}", parse_mode="Markdown")
    try:
        media = [InputMediaPhoto(media=url, caption=f"{k} — {v['name'][lang]} {v['price']}") for k,url in v["plans"].items()]
        await cb.message.answer_media_group(media=media)
    except Exception as e:
        logging.error(e)
        for k,url in v["plans"].items():
            await cb.message.answer_photo(photo=url, caption=k)
    await cb.message.answer(t["menu_hint"], reply_markup=main_menu_kb(lang, villa_id))
    await cb.answer()

@dp.callback_query(F.data.startswith("gallery_"))
async def cb_gallery(cb: types.CallbackQuery):
    villa_id = cb.data.split("_")[1]
    if villa_id not in VILLAS: villa_id=get_villa(cb.from_user.id)
    lang = get_lang(cb.from_user.id)
    v = VILLAS[villa_id]
    t = TEXTS[lang]
    await cb.message.answer(t["gallery_title"].format(villa_name=v["name"][lang]), parse_mode="Markdown")
    try:
        media = [InputMediaPhoto(media=url) for url in v["gallery"]]
        await cb.message.answer_media_group(media=media)
    except:
        await cb.message.answer_photo(photo=v["main"])
    await cb.message.answer(t["menu_hint"], reply_markup=main_menu_kb(lang, villa_id))
    await cb.answer()

@dp.callback_query(F.data.startswith("book_"))
async def cb_book(cb: types.CallbackQuery, state: FSMContext):
    villa_id = cb.data.split("_")[1]
    if villa_id not in VILLAS: villa_id=get_villa(cb.from_user.id)
    USER_VILLA[cb.from_user.id]=villa_id
    lang = get_lang(cb.from_user.id)
    v = VILLAS[villa_id]
    t = TEXTS[lang]
    await state.set_state(BookingForm.name)
    await state.update_data(villa_id=villa_id)
    await cb.message.answer(f"{t['book_title'].format(villa_name=v['name'][lang])}\n\n{t['book_start'].format(villa_name=v['name'][lang])}", parse_mode="Markdown")
    await cb.answer()

@dp.message(BookingForm.name)
async def book_name(m: types.Message, state: FSMContext):
    await state.update_data(name=m.text.strip())
    lang = get_lang(m.from_user.id)
    t = TEXTS[lang]
    await state.set_state(BookingForm.phone)
    await m.answer(t["book_phone"].format(name=m.text.strip()))

@dp.message(BookingForm.phone)
async def book_phone(m: types.Message, state: FSMContext):
    await state.update_data(phone=m.text.strip())
    lang = get_lang(m.from_user.id)
    t = TEXTS[lang]
    await state.set_state(BookingForm.date)
    await m.answer(t["book_date"])

@dp.message(BookingForm.date)
async def book_date(m: types.Message, state: FSMContext):
    await state.update_data(date=m.text.strip())
    lang = get_lang(m.from_user.id)
    t = TEXTS[lang]
    await state.set_state(BookingForm.comment)
    await m.answer(t["book_comment"])

@dp.message(BookingForm.comment)
async def book_comment(m: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = get_lang(m.from_user.id)
    t = TEXTS[lang]
    villa_id = data.get("villa_id", get_villa(m.from_user.id))
    v = VILLAS.get(villa_id, VILLAS["villa01"])
    name = data.get("name","Guest")
    phone = data.get("phone","")
    date = data.get("date","")
    comment = m.text.strip()
    lead = {"name": name, "phone": phone, "email": "", "message": f"Booking {v['name'][lang]} {v['price']}: {comment} | Date: {date}", "booking_date": date, "lang": lang, "villa_id": villa_id, "page_url": "telegram_bot", "session_id": f"{m.from_user.id}_{m.message_id}"}
    path = pathlib.Path(f"/tmp/villas_chats/{lead['session_id']}.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([lead], ensure_ascii=False), encoding='utf-8')
    await notify_admin(lead)
    await m.answer(t["book_confirm_user"].format(name=name, date=date, phone=phone, villa_name=v["name"][lang], price=v["price"]), reply_markup=main_menu_kb(lang, villa_id), parse_mode="Markdown")
    await state.clear()

@dp.message(F.reply_to_message)
async def handle_reply(m: types.Message):
    replied_id = m.reply_to_message.message_id
    lead = SESSIONS.get(replied_id)
    if not lead:
        await m.answer("Session expired")
        return
    session_id = lead.get('session_id')
    path = pathlib.Path(f"/tmp/villas_chats/{session_id}.json")
    history = []
    if path.exists():
        try: history = json.loads(path.read_text(encoding='utf-8'))
        except: pass
    history.append({"from_admin": True, "text": m.text or m.caption or "", "timestamp": m.date.isoformat()})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(history, ensure_ascii=False), encoding='utf-8')
    await m.answer("✅ Sent to client")

async def handle_webhook_update(update_dict: dict):
    update = types.Update.model_validate(update_dict)
    await dp.feed_update(bot, update)
