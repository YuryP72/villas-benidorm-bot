
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
        "basement": {"url": "https://villas-benidorm.com/renders/plans/floor-1.png", "name": "Basement -1"},
        "ground": {"url": "https://villas-benidorm.com/renders/plans/floor0.png", "name": "Ground Floor"},
        "first": {"url": "https://villas-benidorm.com/renders/plans/floor1.png", "name": "First Floor"},
    }
}

SESSIONS: Dict[int, dict] = {}
USER_LANG: Dict[int, str] = {}

class BookingForm(StatesGroup):
    name = State()
    phone = State()
    date = State()
    comment = State()

TEXTS = {
    "en": {
        "welcome_gallery_caption": "Residence Benidorm — Premium Modern Villa 1/5",
        "welcome_title": "💎 Villas Benidorm — Premium Collection\n\nWelcome to Residence, a modern luxury villa on Costa Blanca.",
        "choose_lang": "Please choose your language / Elige tu idioma / Выберите язык:",
        "lang_en": "🇬🇧 English",
        "lang_es": "🇪🇸 Español",
        "lang_ru": "🇷🇺 Русский",
        "lang_set": "Language set to English 🇬🇧",
        "main_menu": "🏡 *Residence — Premium Villa*\n\nWhat would you like to explore?",
        "btn_price": "💶 Price & Details",
        "btn_location": "📍 Location",
        "btn_plans": "🗺️ Floor Plans",
        "btn_gallery": "🖼️ Gallery",
        "btn_book": "📅 Book Viewing",
        "btn_lang": "🌐 Language",
        "price_title": "💶 *Price & Specifications*",
        "price_text": (
            " *Residence Benidorm*\n"
            "Price: *€2,450,000* (VAT not included)\n\n"
            "• Built: 465 m² / Useful: 342 m²\n"
            "• Plot: 1,200 m² — sea view\n"
            "• 4 Bedrooms + 5 Bathrooms\n"
            "• 3 Levels: Basement, Ground, First\n"
            "• Infinity pool 14m, outdoor jacuzzi\n"
            "• Grenton Smart Home, underfloor heating\n"
            "• 2 parking + electric shutters, alarm\n"
            "• A+ energy, triple-glazed aluminium\n"
            "• Panoramic windows, golden hour living\n\n"
            "Ready Q4 2026. Furniture pack optional."
        ),
        "location_title": "📍 *Location*",
        "location_text": (
            " *Finestrat — Benidorm, Costa Blanca*\n"
            "Privileged hilltop position with panoramic views of Mediterranean Sea & Benidorm skyline.\n\n"
            "• 1.2 km to Levante Beach / Playa\n"
            "• 3 min to Finestrat commercial center\n"
            "• 5 min to Terra Mítica, La Cala\n"
            "• 45 min to Alicante Airport (ALC)\n"
            "• 30 min to Altea, 60 min to Valencia\n\n"
            "Quiet residential area Las Villas, yet close to all services. Orientation South-East for all-day sun.\n"
            "Coordinates: 38.56°N, -0.13°W"
        ),
        "plans_title": "🗺️ *Floor Plans — Residence*",
        "plans_text": "Here are the 3 levels directly from our architects. No need to go to website:",
        "gallery_title": "🖼️ *Gallery — 5 Premium Renders*",
        "book_title": "📅 *Book Private Viewing*",
        "book_start": "Great! Let's arrange a private viewing.\n\nWhat is your full name?",
        "book_phone": "Thanks, {name}!\n\nPlease share your phone / WhatsApp (with country code):",
        "book_date": "Perfect.\n\nPreferred date & time for viewing? (e.g. Sep 25, 17:00)",
        "book_comment": "Almost done.\n\nAny preferences? (budget, language of manager: EN/ES/RU, coming from... )",
        "book_confirm_user": "✅ Thank you {name}!\n\nYour request is sent. Our manager will contact you via WhatsApp/phone within 30 minutes.\n\n• Date: {date}\n• Phone: {phone}\n\nWe speak English, Spanish, Russian.",
        "book_admin": "🔥 *NEW BOOKING — Private Viewing*",
        "new_lead": "🔥 New lead from bot",
        "reply_hint": "Reply to this message to answer client directly in chat widget",
        "back": "⬅️ Back to menu",
        "menu_hint": "Choose below:",
    },
    "es": {
        "welcome_gallery_caption": "Residence Benidorm — Villa Moderna Premium 1/5",
        "welcome_title": "💎 Villas Benidorm — Colección Premium\n\nBienvenido a Residence, villa moderna de lujo en Costa Blanca.",
        "choose_lang": "Por favor elige tu idioma / Please choose / Выберите:",
        "lang_en": "🇬🇧 English",
        "lang_es": "🇪🇸 Español",
        "lang_ru": "🇷🇺 Русский",
        "lang_set": "Idioma cambiado a Español 🇪🇸",
        "main_menu": "🏡 *Residence — Villa Premium*\n\n¿Qué te gustaría explorar?",
        "btn_price": "💶 Precio y Detalles",
        "btn_location": "📍 Ubicación",
        "btn_plans": "🗺️ Planos",
        "btn_gallery": "🖼️ Galería",
        "btn_book": "📅 Reservar Visita",
        "btn_lang": "🌐 Idioma",
        "price_title": "💶 *Precio y Especificaciones*",
        "price_text": (
            " *Residence Benidorm*\n"
            "Precio: *2.450.000 €* (IVA no incluido)\n\n"
            "• Construida: 465 m² / Útil: 342 m²\n"
            "• Parcela: 1.200 m² — vistas al mar\n"
            "• 4 Dormitorios + 5 Baños\n"
            "• 3 Plantas: Sótano, Baja, Primera\n"
            "• Piscina infinita 14m, jacuzzi exterior\n"
            "• Casa inteligente Grenton, suelo radiante\n"
            "• 2 parkings + persianas eléctricas, alarma\n"
            "• Energía A+, aluminio triple vidrio\n"
            "• Ventanales panorámicos, living dorado\n\n"
            "Entrega Q4 2026. Pack muebles opcional."
        ),
        "location_title": "📍 *Ubicación*",
        "location_text": (
            " *Finestrat — Benidorm, Costa Blanca*\n"
            "Posición privilegiada en colina con vistas panorámicas al Mediterráneo y skyline de Benidorm.\n\n"
            "• 1,2 km a Playa de Levante\n"
            "• 3 min a centro comercial Finestrat\n"
            "• 5 min a Terra Mítica, La Cala\n"
            "• 45 min a Aeropuerto Alicante (ALC)\n"
            "• 30 min a Altea, 60 min a Valencia\n\n"
            "Residencial tranquilo Las Villas, cerca de todo. Orientación Sur-Este, sol todo el día."
        ),
        "plans_title": "🗺️ *Planos — Residence*",
        "plans_text": "Aquí tienes los 3 niveles directamente, sin ir a la web:",
        "gallery_title": "🖼️ *Galería — 5 Renders Premium*",
        "book_title": "📅 *Reservar Visita Privada*",
        "book_start": "¡Perfecto! Organicemos una visita privada.\n\n¿Cuál es tu nombre completo?",
        "book_phone": "Gracias, {name}!\n\nComparte tu teléfono / WhatsApp (con prefijo):",
        "book_date": "Perfecto.\n\n¿Fecha y hora preferida? (ej. 25 sep, 17:00)",
        "book_comment": "Casi listo.\n\n¿Alguna preferencia? (presupuesto, idioma del gestor: ES/EN/RU...)",
        "book_confirm_user": "✅ ¡Gracias {name}!\n\nTu solicitud está enviada. Nuestro gestor te contactará por WhatsApp/teléfono en 30 minutos.\n\n• Fecha: {date}\n• Tel: {phone}\n\nHablamos Español, English, Русский.",
        "book_admin": "🔥 *NUEVA RESERVA — Visita Privada*",
        "new_lead": "🔥 Nuevo lead del bot",
        "reply_hint": "Responde a este mensaje para contestar al cliente",
        "back": "⬅️ Volver al menú",
        "menu_hint": "Elige abajo:",
    },
    "ru": {
        "welcome_gallery_caption": "Residence Benidorm — Премиальная современная вилла 1/5",
        "welcome_title": "💎 Villas Benidorm — Премиальная коллекция\n\nДобро пожаловать в Residence — современная люкс-вилла на Коста-Бланка.",
        "choose_lang": "Пожалуйста, выберите язык / Please choose / Elige idioma:",
        "lang_en": "🇬🇧 English",
        "lang_es": "🇪🇸 Español",
        "lang_ru": "🇷🇺 Русский",
        "lang_set": "Язык переключен на Русский 🇷🇺",
        "main_menu": "🏡 *Residence — Премиальная вилла*\n\nЧто вы хотите узнать?",
        "btn_price": "💶 Цена и характеристики",
        "btn_location": "📍 Расположение",
        "btn_plans": "🗺️ Планировки",
        "btn_gallery": "🖼️ Галерея",
        "btn_book": "📅 Запись на просмотр",
        "btn_lang": "🌐 Язык",
        "price_title": "💶 *Цена и характеристики*",
        "price_text": (
            " *Residence Benidorm*\n"
            "Цена: *€2 450 000* (без НДС)\n\n"
            "• Построено: 465 м² / Полезная: 342 м²\n"
            "• Участок: 1 200 м² — вид на море\n"
            "• 4 Спальни + 5 Ванных\n"
            "• 3 Уровня: Цоколь, 1 этаж, 2 этаж\n"
            "• Инфинити-бассейн 14м, джакузи\n"
            "• Умный дом Grenton, теплый пол\n"
            "• 2 паркинга + электрожалюзи, сигнализация\n"
            "• Энергоэффективность A+, тройной стеклопакет\n"
            "• Панорамные окна, living в золоте\n\n"
            "Сдача Q4 2026. Меблировка опционально."
        ),
        "location_title": "📍 *Расположение*",
        "location_text": (
            " *Финестрат — Бенидорм, Коста-Бланка*\n"
            "Привилегированная позиция на холме с панорамным видом на Средиземное море и skyline Бенидорма.\n\n"
            "• 1,2 км до пляжа Леванте\n"
            "• 3 мин до торгового центра Финестрат\n"
            "• 5 мин до Terra Mítica, La Cala\n"
            "• 45 мин до аэропорта Аликанте (ALC)\n"
            "• 30 мин до Алтеи, 60 мин до Валенсии\n\n"
            "Тихий жилой комплекс Las Villas, рядом все сервисы. Ориентация Юго-Восток — солнце весь день."
        ),
        "plans_title": "🗺️ *Планировки — Residence*",
        "plans_text": "Вот 3 уровня напрямую от архитекторов, без перехода на сайт:",
        "gallery_title": "🖼️ *Галерея — 5 премиальных рендеров*",
        "book_title": "📅 *Запись на приватный просмотр*",
        "book_start": "Отлично! Давайте организуем приватный просмотр.\n\nКак вас зовут? (полное имя)",
        "book_phone": "Спасибо, {name}!\n\nВаш телефон / WhatsApp (с кодом страны):",
        "book_date": "Принято.\n\nУдобная дата и время просмотра? (например 25 сен, 17:00)",
        "book_comment": "Почти готово.\n\nПожелания? (бюджет, язык менеджера: RU/EN/ES, откуда приедете...)",
        "book_confirm_user": "✅ Спасибо, {name}!\n\nЗаявка отправлена. Менеджер свяжется с вами по WhatsApp/телефону в течение 30 минут.\n\n• Дата: {date}\n• Телефон: {phone}\n\nГоворим на Русском, English, Español.",
        "book_admin": "🔥 *НОВАЯ ЗАПИСЬ — Приватный просмотр*",
        "new_lead": "🔥 Новый лид с бота",
        "reply_hint": "Ответь Reply чтобы написать клиенту на сайт",
        "back": "⬅️ Назад в меню",
        "menu_hint": "Выберите ниже:",
    }
}

def get_lang(uid: int) -> str:
    return USER_LANG.get(uid, "en")

def lang_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton(text="🇪🇸 Español", callback_data="lang_es")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
    ])

def main_menu_kb(lang: str):
    t = TEXTS[lang]
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t["btn_price"], callback_data="price"),
         InlineKeyboardButton(text=t["btn_location"], callback_data="location")],
        [InlineKeyboardButton(text=t["btn_plans"], callback_data="plans"),
         InlineKeyboardButton(text=t["btn_gallery"], callback_data="gallery")],
        [InlineKeyboardButton(text=t["btn_book"], callback_data="book")],
        [InlineKeyboardButton(text=t["btn_lang"], callback_data="change_lang")],
    ])

def back_kb(lang: str):
    t = TEXTS[lang]
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t["back"], callback_data="menu")]
    ])

async def notify_admin(lead: dict):
    lang = lead.get("lang", "en")
    t = TEXTS.get(lang, TEXTS["en"])
    is_booking = "booking_date" in lead and lead.get("booking_date")
    if is_booking:
        text = (
            f"{TEXTS.get(lang, TEXTS['en'])['book_admin']}\n\n"
            f"🏡 Villa: {lead.get('villa_id','residence')}\n"
            f"🌐 Lang: {lead.get('lang')} | {lead.get('page_url','bot')}\n"
            f"👤 {lead.get('name')} | 📞 {lead.get('phone')}\n"
            f"📅 Date: {lead.get('booking_date')}\n"
            f"💬 {lead.get('message')}\n\n"
            f"ID: {lead.get('session_id')}\n_{t['reply_hint']}_"
        )
    else:
        text = (
            f"{t['new_lead']}\n\n"
            f"🏡 Villa: {lead.get('villa_id','residence')}\n"
            f"🌐 Lang: {lead.get('lang')} | {lead.get('page_url','')}\n"
            f"👤 {lead.get('name')} | 📞 {lead.get('phone')} | 📧 {lead.get('email')}\n\n"
            f"💬 {lead.get('message')}\n\n"
            f"ID: {lead.get('session_id')}\n_{t['reply_hint']}_"
        )
    admin_id = os.getenv("ADMIN_CHAT_ID")
    if not admin_id:
        return None
    try:
        msg = await bot.send_message(chat_id=admin_id, text=text, parse_mode="Markdown")
        SESSIONS[msg.message_id] = lead
        SESSIONS[lead.get('session_id')] = lead
        return msg.message_id
    except Exception as e:
        logging.error(f"notify_admin error: {e}")
        return None

@dp.message(Command("start", "villa", "lang"))
async def cmd_start(m: types.Message, state: FSMContext):
    await state.clear()
    uid = m.from_user.id
    default_lang = USER_LANG.get(uid, "en")
    try:
        media = []
        for i, url in enumerate(VILLA["gallery"][:5]):
            cap = TEXTS[default_lang]["welcome_gallery_caption"] if i==0 else None
            media.append(InputMediaPhoto(media=url, caption=cap))
        await m.answer_media_group(media=media)
    except Exception as e:
        logging.error(f"gallery send error {e}")
        await m.answer_photo(photo=VILLA["main"], caption=TEXTS[default_lang]["welcome_gallery_caption"])
    t = TEXTS[default_lang]
    await m.answer(f"{t['welcome_title']}\n\n{t['choose_lang']}", reply_markup=lang_kb())

@dp.callback_query(F.data.startswith("lang_"))
async def cb_set_lang(cb: types.CallbackQuery):
    lang = cb.data.split("_")[1]
    if lang not in TEXTS:
        lang = "en"
    USER_LANG[cb.from_user.id] = lang
    t = TEXTS[lang]
    await cb.answer(t["lang_set"])
    await cb.message.answer(t["lang_set"] + f"\n\n{t['main_menu']}\n\n{t['menu_hint']}", reply_markup=main_menu_kb(lang), parse_mode="Markdown")

@dp.callback_query(F.data == "change_lang")
async def cb_change_lang(cb: types.CallbackQuery):
    uid = cb.from_user.id
    lang = get_lang(uid)
    t = TEXTS[lang]
    await cb.message.answer(t["choose_lang"], reply_markup=lang_kb())
    await cb.answer()

@dp.callback_query(F.data == "menu")
async def cb_menu(cb: types.CallbackQuery):
    lang = get_lang(cb.from_user.id)
    t = TEXTS[lang]
    await cb.message.answer(t["main_menu"], reply_markup=main_menu_kb(lang), parse_mode="Markdown")
    await cb.answer()

@dp.callback_query(F.data == "price")
async def cb_price(cb: types.CallbackQuery):
    lang = get_lang(cb.from_user.id)
    t = TEXTS[lang]
    await cb.message.answer(f"{t['price_title']}\n\n{t['price_text']}", reply_markup=back_kb(lang), parse_mode="Markdown")
    await cb.answer()

@dp.callback_query(F.data == "location")
async def cb_location(cb: types.CallbackQuery):
    lang = get_lang(cb.from_user.id)
    t = TEXTS[lang]
    await cb.message.answer(f"{t['location_title']}\n\n{t['location_text']}", reply_markup=back_kb(lang), parse_mode="Markdown")
    await cb.answer()

@dp.callback_query(F.data == "plans")
async def cb_plans(cb: types.CallbackQuery):
    lang = get_lang(cb.from_user.id)
    t = TEXTS[lang]
    await cb.message.answer(f"{t['plans_title']}\n\n{t['plans_text']}", parse_mode="Markdown")
    try:
        media = [
            InputMediaPhoto(media=VILLA["plans"]["basement"]["url"], caption=f"Basement -1 / Sótano -1 / Цоколь -1"),
            InputMediaPhoto(media=VILLA["plans"]["ground"]["url"], caption=f"Ground Floor / Planta Baja / 1 этаж"),
            InputMediaPhoto(media=VILLA["plans"]["first"]["url"], caption=f"First Floor / Planta Primera / 2 этаж"),
        ]
        await cb.message.answer_media_group(media=media)
    except Exception as e:
        logging.error(f"plans error {e}")
        for key in ["basement","ground","first"]:
            await cb.message.answer_photo(photo=VILLA["plans"][key]["url"], caption=VILLA["plans"][key]["name"])
    await cb.message.answer(t["menu_hint"], reply_markup=main_menu_kb(lang))
    await cb.answer()

@dp.callback_query(F.data == "gallery")
async def cb_gallery(cb: types.CallbackQuery):
    lang = get_lang(cb.from_user.id)
    t = TEXTS[lang]
    await cb.message.answer(t["gallery_title"], parse_mode="Markdown")
    try:
        media = [InputMediaPhoto(media=url) for url in VILLA["gallery"]]
        await cb.message.answer_media_group(media=media)
    except Exception as e:
        logging.error(f"gallery error {e}")
        await cb.message.answer_photo(photo=VILLA["main"])
    await cb.message.answer(t["menu_hint"], reply_markup=main_menu_kb(lang))
    await cb.answer()

@dp.callback_query(F.data == "book")
async def cb_book(cb: types.CallbackQuery, state: FSMContext):
    lang = get_lang(cb.from_user.id)
    t = TEXTS[lang]
    await state.set_state(BookingForm.name)
    await cb.message.answer(f"{t['book_title']}\n\n{t['book_start']}", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t["back"], callback_data="menu")]]))
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
    name = data.get("name","Guest")
    phone = data.get("phone","")
    date = data.get("date","")
    comment = m.text.strip()
    lead = {
        "name": name,
        "phone": phone,
        "email": "",
        "message": f"Booking: {comment} | Date: {date}",
        "booking_date": date,
        "lang": lang,
        "villa_id": "residence",
        "page_url": "telegram_bot",
        "session_id": f"{m.from_user.id}_{m.message_id}",
    }
    path = pathlib.Path(f"/tmp/villas_chats/{lead['session_id']}.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([lead], ensure_ascii=False), encoding='utf-8')
    await notify_admin(lead)
    await m.answer(t["book_confirm_user"].format(name=name, date=date, phone=phone), reply_markup=main_menu_kb(lang), parse_mode="Markdown")
    await state.clear()

@dp.message(F.reply_to_message)
async def handle_reply(m: types.Message):
    replied_id = m.reply_to_message.message_id
    lead = SESSIONS.get(replied_id)
    if not lead:
        await m.answer("Session expired — bot restarted. /tmp cleared.")
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
