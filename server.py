
import os, uuid, json, pathlib, logging
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()
from bot import bot, handle_webhook_update, notify_admin, VILLAS, TEXTS

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Villas Benidorm - v8 diagnostic")
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
    return {"status": "ok", "version": "v8-diagnostic-442261830", "villas": list(VILLAS.values())}

@app.get("/api/debug_env")
async def debug_env():
    admin = os.getenv("ADMIN_CHAT_ID") or ""
    token = os.getenv("BOT_TOKEN") or ""
    webhook = os.getenv("WEBHOOK_URL") or ""
    def mask(v):
        if not v: return "NOT SET"
        v=v.strip()
        if len(v)<=4: return "****"
        return v[:2]+"****"+v[-2:]+" (len="+str(len(v))+")"
    return {
        "ADMIN_CHAT_ID_masked": mask(admin),
        "ADMIN_CHAT_ID_raw_len": len(admin.strip()) if admin else 0,
        "ADMIN_CHAT_ID_is_numeric": admin.strip().isdigit() if admin else False,
        "ADMIN_CHAT_ID_should_be": "442261830 for Yury",
        "BOT_TOKEN_set": bool(token),
        "WEBHOOK_URL": webhook,
    }

@app.get("/api/bot_info")
async def bot_info():
    try:
        me = await bot.get_me()
        return {"ok": True, "username": f"@{me.username}", "id": me.id, "link": f"https://t.me/{me.username}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.get("/api/test_admin")
async def test_admin():
    admin_id = os.getenv("ADMIN_CHAT_ID")
    if not admin_id:
        return {"ok": False, "error": "ADMIN_CHAT_ID not set in Render env vars"}
    test_lead = {"name": "Test Lead Yury", "phone": "+34 600 000 000", "message": "Test from /api/test_admin - ID 442261830 - if you see this, ADMIN works!", "booking_date": "2027 test", "lang": "en", "villa_id": "villa02", "page_url": "test_admin", "session_id": "test123"}
    try:
        result = await notify_admin(test_lead)
        if result:
            return {"ok": True, "msg_id": result, "admin_id": admin_id.strip(), "note": "Check Telegram NOW - message should have arrived!"}
        else:
            return {"ok": False, "admin_id": admin_id.strip(), "error": "notify_admin returned None - check Render Logs for 'notify_admin FAILED'"}
    except Exception as e:
        return {"ok": False, "admin_id": admin_id.strip() if admin_id else None, "error": str(e)}

@app.get("/api/villas")
async def get_villas():
    return {"villas": list(VILLAS.values())}

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

@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if secret and secret != os.getenv("WEBHOOK_SECRET"):
        raise HTTPException(403, "bad secret")
    data = await request.json()
    background_tasks.add_task(handle_webhook_update, data)
    return {"ok": True}

@app.on_event("startup")
async def on_startup():
    url = os.getenv("WEBHOOK_URL")
    if url:
        try:
            await bot.set_webhook(url=f"{url.rstrip('/')}/webhook", secret_token=os.getenv("WEBHOOK_SECRET"))
            print(f"Webhook set to {url}/webhook - v8")
        except Exception as e:
            print(f"Webhook error: {e}")
