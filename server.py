
import os, uuid, json, pathlib
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
from bot import bot, handle_webhook_update, notify_admin, VILLA, TEXTS

app = FastAPI(title="Villas Benidorm - Premium API v2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ContactRequest(BaseModel):
    name: str
    phone: str = ""
    email: str = ""
    message: str
    lang: str = "en"
    villa_id: str = "residence"
    page_url: str = ""
    session_id: str = ""
    honeypot: str = ""
    booking_date: str = ""

STORAGE = pathlib.Path("/tmp/villas_chats")
STORAGE.mkdir(parents=True, exist_ok=True)

VILLA_FULL = {
    **VILLA,
    "price": {"en": "€2,450,000 (VAT not included)", "es": "2.450.000 € (IVA no incluido)", "ru": "€2 450 000 (без НДС)"},
    "specs": {"en": "465 m² built / 342 m² useful / 1,200 m² plot / 4 bed / 5 bath / Infinity pool 14m / Smart Home Grenton / A+", "es": "465 m² construidos / 342 m² útiles / 1.200 m² parcela / 4 dorm / 5 baños / Piscina infinita 14m / Casa inteligente Grenton / A+", "ru": "465 м² построено / 342 м² полезной / 1 200 м² участок / 4 спальни / 5 ванных / Бассейн 14м / Умный дом Grenton / A+"},
    "location": {"en": "Finestrat-Benidorm, Costa Blanca — hilltop, 1.2km to Levante Beach, 45min to Alicante Airport", "es": "Finestrat-Benidorm, Costa Blanca — en colina, 1,2km a Playa Levante, 45min a Aeropuerto Alicante", "ru": "Финестрат-Бенидорм, Коста-Бланка — на холме, 1,2км до пляжа Леванте, 45мин до аэропорта Аликанте"},
    "details": TEXTS
}

@app.get("/")
async def root():
    return {"status": "ok", "version": "v2-premium", "villa": VILLA_FULL}

@app.get("/api/villas")
async def get_villas():
    return {"villas": [VILLA_FULL]}

@app.get("/api/villa/{villa_id}/gallery")
async def gallery(villa_id: str):
    return {"gallery": VILLA["gallery"], "main": VILLA["main"]}

@app.get("/api/villa/{villa_id}/plans")
async def plans(villa_id: str):
    return VILLA["plans"]

@app.get("/api/villa/{villa_id}/info")
async def villa_info(villa_id: str, lang: str = "en"):
    l = lang if lang in ["en","es","ru"] else "en"
    return {"price": VILLA_FULL["price"][l], "specs": VILLA_FULL["specs"][l], "location": VILLA_FULL["location"][l], "gallery": VILLA["gallery"], "plans": VILLA["plans"], "texts": TEXTS[l]}

@app.post("/api/contact")
async def contact(req: ContactRequest, background_tasks: BackgroundTasks):
    if req.honeypot:
        raise HTTPException(400, "spam")
    session_id = req.session_id or str(uuid.uuid4())[:8]
    req.session_id = session_id
    path = STORAGE / f"{session_id}.json"
    history = []
    if path.exists():
        try: history = json.loads(path.read_text(encoding='utf-8'))
        except: history = []
    history.append({"from_admin": False, "text": req.message, "name": req.name, "phone": req.phone, "booking_date": req.booking_date, "timestamp": "now", "lang": req.lang})
    path.write_text(json.dumps(history, ensure_ascii=False), encoding='utf-8')
    background_tasks.add_task(notify_admin, req.model_dump())
    return {"ok": True, "session_id": session_id}

@app.get("/api/chat/{session_id}")
async def get_chat(session_id: str):
    path = STORAGE / f"{session_id}.json"
    if not path.exists():
        return {"messages": []}
    try:
        return {"messages": json.loads(path.read_text(encoding='utf-8'))}
    except:
        return {"messages": []}

@app.post("/webhook")
async def webhook(request: Request):
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if secret and secret != os.getenv("WEBHOOK_SECRET"):
        raise HTTPException(403, "bad secret")
    data = await request.json()
    await handle_webhook_update(data)
    return {"ok": True}

@app.on_event("startup")
async def on_startup():
    url = os.getenv("WEBHOOK_URL")
    if url:
        try:
            await bot.set_webhook(url=f"{url.rstrip('/')}/webhook", secret_token=os.getenv("WEBHOOK_SECRET"))
            print(f"Webhook set to {url}/webhook")
        except Exception as e:
            print(f"Webhook error: {e}")
