import time
from collections import defaultdict, deque
from pyrogram import filters
from pyrogram.types import ChatPermissions
from security import is_allowed

async def _enabled(app, message, feature, default=True):
    v=await app.settings.get(message.chat.id,feature,"enabled",default)
    return bool(v)

def register_message_handlers(app):
    app.spam_cache=defaultdict(lambda:defaultdict(deque))
    app.quiz_answers={}

    @app.on_message(filters.group & filters.text)
    async def group_text(_,m):
        if not m.from_user or not m.text or m.text.startswith("."): return

        # Quiz answer
        ans=app.quiz_answers.get(m.chat.id)
        if ans and m.from_user.id==ans[1]:
            if m.text.strip().lower()==ans[0]:
                await app.db.score_add(m.chat.id,m.from_user.id,m.from_user.first_name or "User",points=10,xp=10)
                await m.reply_text("✅ Jawaban benar! +10 poin.")
                app.quiz_answers.pop(m.chat.id,None)
                return

        # Anti-spam
        if await is_allowed(app,m,"antispam") and await _enabled(app,m,"antispam",False):
            now=time.monotonic(); q=app.spam_cache[m.chat.id][m.from_user.id]
            q.append(now)
            while q and now-q[0]>10: q.popleft()
            if len(q)>=8:
                try:
                    await app.restrict_chat_member(m.chat.id,m.from_user.id,ChatPermissions())
                    await m.reply_text("🛡️ Spam terdeteksi, user dimute sementara.")
                    q.clear()
                except Exception: pass

        if await is_allowed(app,m,"autoreply") and await _enabled(app,m,"autoreply",True):
            response=await app.db.find_autoreply(m.chat.id,m.text)
            if response: await m.reply_text(response)
