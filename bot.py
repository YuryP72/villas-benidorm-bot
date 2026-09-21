
import os, json, logging, pathlib
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from typing import Dict

logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

VILLAS = {
    "villa01": {
        "id": "villa01",
        "name": {"en": "VILLA 01", "es": "VILLA 01", "ru": "VILLA 01"},
        "full_name": {"en": "VILLA 01 — Premium", "es": "VILLA 01 — Premium", "ru": "VILLA 01 — Premium"},
        "built": "470 M²", "beds": "5 BED",
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
        "built": "470 M²", "beds": "5 BED",
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
        "built": "470 M²", "beds": "5 BED",
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
        "welcome_title": "Villas Benidorm — villas-benidorm.com\n\n3 exclusive modern villas — 470 M2 • 5 BED each.\nPrices as on website.",
        "choose_lang": "Please choose your language / Elige tu idioma / Выберите язык:",
        "lang_en": "English", "lang_es": "Espanol", "lang_ru": "Русский",
        "lang_set": "Language: English",
        "choose_villa": "Choose villa — prices as on villas-benidorm.com:\n\nVILLA 01 — €2,725,000 — 470 M2 • 5 BED\nVILLA 02 — €2,885,000 — 470 M2 • 5 BED\nVILLA 03 — €2,835,000 — 470 M2 • 5 BED\n\nDelivery: 2027",
        "main_menu": "VILLA {villa_name} — {price}\n470 M2 • 5 BED • Delivery 2027",
        "btn_price": "Price", "btn_location": "Location", "btn_plans": "Plans", "btn_gallery": "Gallery", "btn_book": "Book Viewing", "btn_lang": "Language", "btn_villas": "All 3 Villas",
        "price_title": "{villa_name} — {price}",
        "price_text": "{villa_name}\nPrice: {price} — as on villas-benidorm.com\n\nBuilt: {built} • {beds_detail}\nPlot: sea view, infinity pool 14m\nSmart Home, underfloor heating\nA+ energy, triple-glazed\n\nDelivery: {delivery}",
        "location_title": "Location", "location_text": "Finestrat — Benidorm, Costa Blanca\nHilltop, panoramic sea & skyline\n1.2 km to Levante Beach\n3 min to Finestrat center\n45 min to Alicante Airport",
        "plans_title": "{villa_name} — Plans", "plans_text": "Floor plans:", "gallery_title": "{villa_name} — Gallery", "book_title": "Book {villa_name}",
        "book_start": "Viewing {villa_name} {price}\n\nYour name?", "book_phone": "Thanks {name}! Phone / WhatsApp:", "book_date": "Preferred date & time?", "book_comment": "Preferences? (EN/ES/RU)",
        "book_confirm_user": "Thank you {name}!\n\nRequest for {villa_name} {price} sent.\nDate: {date}\nPhone: {phone}\nManager will contact in 30 min.",
        "book_admin": "NEW BOOKING", "new_lead": "New lead", "reply_hint": "Reply to answer", "back": "Back", "menu_hint": "Choose:", "villas_list": "3 Villas from villas-benidorm.com:"
    },
    "es": {
        "welcome_title": "Villas Benidorm — villas-benidorm.com\n\n3 villas exclusivas — 470 M2 • 5 DORM",
        "choose_lang": "Elige tu idioma:", "lang_en": "English", "lang_es": "Espanol", "lang_ru": "Русский",
        "lang_set": "Idioma: Espanol",
        "choose_villa": "Elige villa — precios como en villas-benidorm.com:\n\nVILLA 01 — €2,725,000\nVILLA 02 — €2,885,000\nVILLA 03 — €2,835,000\n\nEntrega: 2027",
        "main_menu": "{villa_name} — {price}", "btn_price": "Precio", "btn_location": "Ubicacion", "btn_plans": "Planos", "btn_gallery": "Galeria", "btn_book": "Reservar", "btn_lang": "Idioma", "btn_villas": "Las 3 Villas",
        "price_title": "{villa_name} — {price}", "price_text": "{villa_name}\nPrecio: {price}\n\n{built} • {beds_detail}\nPiscina infinita, Smart Home\nA+, triple vidrio\n\nEntrega: {delivery}",
        "location_title": "Ubicacion", "location_text": "Finestrat — Benidorm\n1,2 km a Playa Levante\n45 min a Alicante\nEntrega 2027",
        "plans_title": "{villa_name}", "plans_text": "Planos:", "gallery_title": "{villa_name}", "book_title": "Reservar {villa_name}",
        "book_start": "Visita {villa_name} {price}\n\nNombre?", "book_phone": "Telefono:", "book_date": "Fecha?", "book_comment": "Preferencias?",
        "book_confirm_user": "Gracias {name}!\n\nSolicitud {villa_name} {price} enviada.\nFecha: {date}\nTel: {phone}",
        "book_admin": "NUEVA RESERVA", "new_lead": "Nuevo lead", "reply_hint": "Responde", "back": "Volver", "menu_hint": "Elige:", "villas_list": "3 Villas:"
    },
    "ru": {
        "welcome_title": "Villas Benidorm — villas-benidorm.com\n\n3 эксклюзивные виллы — 470 M2 • 5 спален",
        "choose_lang": "Выберите язык:", "lang_en": "English", "lang_es": "Espanol", "lang_ru": "Русский",
        "lang_set": "Язык: Русский",
        "choose_villa": "Выберите виллу — цены как на villas-benidorm.com:\n\nVILLA 01 — €2,725,000\nVILLA 02 — €2,885,000\nVILLA 03 — €2,835,000\n\nСдача: 2027",
        "main_menu": "{villa_name} — {price}", "btn_price": "Цена", "btn_location": "Локация", "btn_plans": "Планы", "btn_gallery": "Галерея", "btn_book": "Запись", "btn_lang": "Язык", "btn_villas": "Все 3 виллы",
        "price_title": "{villa_name} — {price}", "price_text": "{villa_name}\nЦена: {price}\n\n{built} • {beds_detail}\nБассейн, умный дом\nA+, тройной стеклопакет\n\nСдача: {delivery}",
        "location_title": "Расположение", "location_text": "Финестрат — Бенидорм\n1,2 км до пляжа\n45 мин до Аликанте\nСдача 2027",
        "plans_title": "{villa_name}", "plans_text": "Планировки:", "gallery_title": "{villa_name}", "book_title": "Запись {villa_name}",
        "book_start": "Запись на {villa_name} {price}\n\nИмя?", "book_phone": "Телефон:", "book_date": "Дата и время?", "book_comment": "Пожелания?",
        "book_confirm_user": "Спасибо {name}!\n\nЗаявка {villa_name} {price} отправлена.\nДата: {date}\nТел: {phone}",
        "book_admin": "НОВАЯ ЗАПИСЬ", "new_lead": "Новый лид", "reply_hint": "Ответь Reply", "back": "Назад", "menu_hint": "Выберите:", "villas_list": "3 виллы:"
    }
}

def get_lang(uid: int) -> str:
    return USER_LANG.get(uid, "en")

def get_villa(uid: int) -> str:
    return USER_VILLA.get(uid, "villa01")

def lang_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="English", callback_data="lang_en")],
        [InlineKeyboardButton(text="Espanol", callback_data="lang_es")],
        [InlineKeyboardButton(text="Русский", callback_data="lang_ru")],
    ])

def villas_kb(lang: str, current_villa_id: str = None):
    rows = []
    for vid in ["villa01", "villa02", "villa03"]:
        v = VILLAS[vid]
        rows.append([InlineKeyboardButton(text=f"{v['name'][lang]} - {v['price']} - {v['built']}", callback_data=f"villa_{vid}")])
    if current_villa_id and current_villa_id in VILLAS:
        v = VILLAS[current_villa_id]
        back_text = TEXTS[lang]["back"] + f" to {v['name'][lang]}"
        rows.append([InlineKeyboardButton(text=back_text, callback_data=f"villa_{current_villa_id}")])
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
        villa_name = v["name"].get(lang, v["name"]["en"])
        text = (
            f"{t['book_admin']} {villa_name} {v['price']}\n"
            f"Villa: {villa_id} | {v['price']}\n"
            f"Lang: {lead.get('lang')}\n"
            f"Name: {lead.get('name')} | Phone: {lead.get('phone')}\n"
            f"Date: {lead.get('booking_date')}\n"
            f"Msg: {lead.get('message')}\n"
            f"ID: {lead.get('session_id')}"
        )
    else:
        villa_name = v["name"].get(lang, v["name"]["en"])
        text = (
            f"{t['new_lead']} {villa_name} {v['price']}\n"
            f"Villa: {villa_id}\n"
            f"Lang: {lead.get('lang')}\n"
            f"Name: {lead.get('name')} | Phone: {lead.get('phone')}\n"
            f"Msg: {lead.get('message')}\n"
            f"ID: {lead.get('session_id')}"
        )
    admin_id_raw = os.getenv("ADMIN_CHAT_ID")
    if not admin_id_raw:
        logging.error("ADMIN_CHAT_ID not set!")
        return None
    try:
        admin_id = int(str(admin_id_raw).strip())
    except Exception:
        admin_id = admin_id_raw
    logging.info(f"notify_admin trying {admin_id} lead {lead.get('session_id')}")
    try:
        msg = await bot.send_message(chat_id=admin_id, text=text)
        SESSIONS[msg.message_id] = lead
        SESSIONS[lead.get("session_id")] = lead
        logging.info(f"Admin notified {admin_id} msg {msg.message_id}")
        return msg.message_id
    except Exception as e:
        logging.error(f"notify_admin FAILED for {admin_id}: {e}")
        return None

@dp.message(Command("start", "villa", "lang"))
async def cmd_start(m: types.Message, state: FSMContext):
    await state.clear()
    uid = m.from_user.id
    default_lang = USER_LANG.get(uid, "en")
    t = TEXTS[default_lang]
    try:
        await m.answer_photo(photo=VILLAS["villa01"]["main"], caption=f"{t['welcome_title']}\n\n{t['choose_lang']}", reply_markup=lang_kb())
    except Exception as e:
        logging.error(f"start photo error {e}")
        await m.answer(f"{t['welcome_title']}\n\n{t['choose_lang']}", reply_markup=lang_kb())

@dp.callback_query(F.data.startswith("lang_"))
async def cb_set_lang(cb: types.CallbackQuery):
    await cb.answer()
    lang = cb.data.split("_")[1]
    if lang not in TEXTS:
        lang = "en"
    USER_LANG[cb.from_user.id] = lang
    t = TEXTS[lang]
    await cb.message.answer(t["choose_villa"], reply_markup=villas_kb(lang), parse_mode="Markdown")

@dp.callback_query(F.data == "change_lang")
async def cb_change_lang(cb: types.CallbackQuery):
    await cb.answer()
    lang = get_lang(cb.from_user.id)
    t = TEXTS[lang]
    await cb.message.answer(t["choose_lang"], reply_markup=lang_kb())

@dp.callback_query(F.data == "all_villas")
async def cb_all_villas(cb: types.CallbackQuery):
    await cb.answer()
    lang = get_lang(cb.from_user.id)
    current_vid = get_villa(cb.from_user.id)
    t = TEXTS[lang]
    await cb.message.answer(t["villas_list"] + "\n\n" + t["choose_villa"], reply_markup=villas_kb(lang, current_vid), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("villa_"))
async def cb_villa(cb: types.CallbackQuery):
    await cb.answer()
    villa_id = cb.data.split("_")[1]
    if villa_id not in VILLAS:
        villa_id = "villa01"
    USER_VILLA[cb.from_user.id] = villa_id
    lang = get_lang(cb.from_user.id)
    v = VILLAS[villa_id]
    t = TEXTS[lang]
    await cb.message.answer(t["main_menu"].format(villa_name=v["name"][lang], price=v["price"]), reply_markup=main_menu_kb(lang, villa_id), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("price_"))
async def cb_price(cb: types.CallbackQuery):
    await cb.answer()
    villa_id = cb.data.split("_")[1]
    if villa_id not in VILLAS:
        villa_id = get_villa(cb.from_user.id)
    lang = get_lang(cb.from_user.id)
    v = VILLAS[villa_id]
    t = TEXTS[lang]
    text = t["price_text"].format(villa_name=v["name"][lang], price=v["price"], built=v["built"], beds_detail=v["beds_detail"][lang], delivery=v["delivery"])
    await cb.message.answer(f"{t['price_title'].format(villa_name=v['name'][lang])}\n\n{text}", reply_markup=back_to_villa_kb(lang, villa_id), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("loc_"))
async def cb_loc(cb: types.CallbackQuery):
    await cb.answer()
    villa_id = cb.data.split("_")[1]
    if villa_id not in VILLAS:
        villa_id = get_villa(cb.from_user.id)
    lang = get_lang(cb.from_user.id)
    t = TEXTS[lang]
    await cb.message.answer(f"{t['location_title']}\n\n{t['location_text']}", reply_markup=back_to_villa_kb(lang, villa_id), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("plans_"))
async def cb_plans(cb: types.CallbackQuery):
    await cb.answer()
    villa_id = cb.data.split("_")[1]
    if villa_id not in VILLAS:
        villa_id = get_villa(cb.from_user.id)
    lang = get_lang(cb.from_user.id)
    v = VILLAS[villa_id]
    t = TEXTS[lang]
    await cb.message.answer(f"{t['plans_title'].format(villa_name=v['name'][lang])}\n\n{t['plans_text']}", parse_mode="Markdown")
    for k, url in v["plans"].items():
        try:
            await cb.message.answer_photo(photo=url, caption=f"{k} - {v['name'][lang]} {v['price']}")
        except Exception as e:
            logging.error(f"plan photo error {e}")
    await cb.message.answer(t["menu_hint"], reply_markup=main_menu_kb(lang, villa_id))

@dp.callback_query(F.data.startswith("gallery_"))
async def cb_gallery(cb: types.CallbackQuery):
    await cb.answer()
    villa_id = cb.data.split("_")[1]
    if villa_id not in VILLAS:
        villa_id = get_villa(cb.from_user.id)
    lang = get_lang(cb.from_user.id)
    v = VILLAS[villa_id]
    t = TEXTS[lang]
    await cb.message.answer(t["gallery_title"].format(villa_name=v["name"][lang]), parse_mode="Markdown")
    for url in v["gallery"][:3]:
        try:
            await cb.message.answer_photo(photo=url)
        except Exception as e:
            logging.error(f"gallery photo error {e}")
    await cb.message.answer(t["menu_hint"], reply_markup=main_menu_kb(lang, villa_id))

@dp.callback_query(F.data.startswith("book_"))
async def cb_book(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer()
    villa_id = cb.data.split("_")[1]
    if villa_id not in VILLAS:
        villa_id = get_villa(cb.from_user.id)
    USER_VILLA[cb.from_user.id] = villa_id
    lang = get_lang(cb.from_user.id)
    v = VILLAS[villa_id]
    t = TEXTS[lang]
    await state.set_state(BookingForm.name)
    await state.update_data(villa_id=villa_id)
    await cb.message.answer(f"{t['book_title'].format(villa_name=v['name'][lang])}\n\n{t['book_start'].format(villa_name=v['name'][lang], price=v['price'])}", parse_mode="Markdown")

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
    name = data.get("name", "Guest")
    phone = data.get("phone", "")
    date = data.get("date", "")
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
        try:
            history = json.loads(path.read_text(encoding='utf-8'))
        except Exception:
            pass
    history.append({"from_admin": True, "text": m.text or m.caption or "", "timestamp": m.date.isoformat()})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(history, ensure_ascii=False), encoding='utf-8')
    await m.answer("Sent to client")

async def handle_webhook_update(update_dict: dict):
    update = types.Update.model_validate(update_dict)
    await dp.feed_update(bot, update)
