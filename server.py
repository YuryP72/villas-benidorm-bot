
import os, uuid, json, pathlib
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()
from bot import bot, handle_webhook_update, notify_admin, VILLAS, TEXTS

app = FastAPI(title="Villas Benidorm - Exact Prices from site v4")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class ContactRequest(BaseModel):
    name: str
    phone: str = ""
    email: str = ""
    message: str
    lang: str = "en"
    villa_id: str = "villa01"
    page_url: str = ""
    session_id: str = ""
    honeypot: str = ""
    booking_date: str = ""

STORAGE = pathlib.Path("/tmp/villas_chats")
STORAGE.mkdir(parents=True, exist_ok=True)

@app.get("/")
async def root():
    return {"status": "ok", "version": "v4-exact-villas-benidorm.com", "villas": list(VILLAS.values())}

@app.get("/api/villas")
async def get_villas():
    return {"villas": list(VILLAS.values())}

@app.get("/api/villa/{villa_id}/gallery")
async def gallery(villa_id: str):
    v = VILLAS.get(villa_id, VILLAS["villa01"])
    return {"gallery": v["gallery"], "main": v["main"]}

@app.get("/api/villa/{villa_id}/plans")
async def plans(villa_id: str):
    v = VILLAS.get(villa_id, VILLAS["villa01"])
    return v["plans"]

@app.get("/api/villa/{villa_id}/info")
async def info(villa_id: str, lang: str = "en"):
    l = lang if lang in ["en","es","ru"] else "en"
    v = VILLAS.get(villa_id, VILLAS["villa01"])
    return {"id": villa_id, "name": v["name"][l], "price": v["price"], "built": v["built"], "beds": v["beds"], "delivery": v["delivery"], "gallery": v["gallery"], "plans": v["plans"], "texts": TEXTS[l]}

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
    history.append({"from_admin": False, "text": req.message, "name": req.name, "phone": req.phone, "booking_date": req.booking_date, "timestamp": "now", "lang": req.lang, "villa_id": req.villa_id})
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
