import io, random, time, urllib.parse
from pyrogram import filters
from pyrogram.types import ChatPermissions
from security import command_allowed, is_allowed
from features import FEATURES

async def _owner(app,m): return bool(m.from_user and await app.db.get_role(m.from_user.id)=="owner")

def register_handlers(app):
    @app.on_message(filters.command(["menu","help"], prefixes="."))
    async def menu(_,m):
        if not await command_allowed(app,m,"menu"): return
        from ui import main_menu
        await m.reply_text(f"🤖 <b>{app.cfg.bot_name}</b>\n\n📋 <b>Semua Fitur</b>\nPilih kategori di bawah:", reply_markup=main_menu(await _owner(app,m)))

    @app.on_message(filters.command(["ban","unban","mute","unmute"], prefixes=".") & filters.group)
    async def moderation(_,m):
        cmd=m.command[0].lower()
        if not await command_allowed(app,m,cmd): return
        target=m.reply_to_message.from_user if m.reply_to_message and m.reply_to_message.from_user else None
        if not target and len(m.command)>1:
            try: target=await app.get_users(m.command[1])
            except Exception: target=None
        if not target: return await m.reply_text("Reply pesan target atau gunakan <code>.ban @username</code>.")
        try:
            if cmd=="ban": await app.ban_chat_member(m.chat.id,target.id)
            elif cmd=="unban": await app.unban_chat_member(m.chat.id,target.id)
            elif cmd=="mute": await app.restrict_chat_member(m.chat.id,target.id,ChatPermissions())
            else: await app.restrict_chat_member(m.chat.id,target.id,ChatPermissions(can_send_messages=True,can_send_media_messages=True,can_send_other_messages=True,can_add_web_page_previews=True))
            await m.reply_text(f"✅ {cmd.capitalize()} berhasil.")
        except Exception as e:
            await m.reply_text(f"❌ Gagal: <code>{type(e).__name__}</code>")

    @app.on_message(filters.command("pay", prefixes="."))
    async def pay(_,m):
        if not await command_allowed(app,m,"pay"): return
        p=await app.db.get_payment(app.cfg.owner_id)
        if not p: return await m.reply_text("💳 Payment belum diatur.")
        text="💳 <b>PEMBAYARAN</b>\n\n"
        if p["bank"] and p["account_number"]: text+=f"🏦 {p['bank']} — <code>{p['account_number']}</code>\n"
        if p["account_name"]: text+=f"👤 A/N: <b>{p['account_name']}</b>\n"
        if p["ewallet"] and p["ewallet_number"]: text+=f"📱 {p['ewallet']}: <code>{p['ewallet_number']}</code>\n"
        if p["description"]: text+=f"\n📝 {p['description']}"
        if p["qris_file_id"]: await m.reply_photo(p["qris_file_id"],caption=text)
        else: await m.reply_text(text)

    @app.on_message(filters.command("setpay", prefixes="."))
    async def setpay(_,m):
        if not await _owner(app,m): return
        a=m.text.split(maxsplit=2)
        if len(a)<3: return await m.reply_text("Format: <code>.setpay bank BCA</code>")
        mp={"bank":"bank","rekening":"account_number","nama":"account_name","ewallet":"ewallet","ewallet_no":"ewallet_number","desc":"description"}
        if a[1] not in mp: return await m.reply_text("Key: bank, rekening, nama, ewallet, ewallet_no, desc")
        await app.db.set_payment(app.cfg.owner_id,**{mp[a[1]]:a[2]}); await m.reply_text("✅ Payment diperbarui.")

    @app.on_message(filters.command("setqris", prefixes="."))
    async def setqris(_,m):
        if not await _owner(app,m): return
        if not m.reply_to_message or not m.reply_to_message.photo: return await m.reply_text("Reply foto QRIS dengan <code>.setqris</code>.")
        await app.db.set_payment(app.cfg.owner_id,qris_file_id=m.reply_to_message.photo.file_id)
        await m.reply_text("✅ QRIS tersimpan.")

    @app.on_message(filters.command("setadmin", prefixes="."))
    async def setadmin(_,m):
        if not await _owner(app,m): return
        target=m.reply_to_message.from_user.id if m.reply_to_message and m.reply_to_message.from_user else None
        if not target and len(m.command)>1 and m.command[1].isdigit(): target=int(m.command[1])
        if not target: return await m.reply_text("Reply user atau <code>.setadmin USER_ID</code>.")
        await app.db.set_role(target,"admin"); await m.reply_text("✅ Admin ditambahkan.")

    @app.on_message(filters.command(["allow","deny"], prefixes="."))
    async def permission(_,m):
        if not await _owner(app,m): return
        if len(m.command)<3 or m.command[1] not in FEATURES or m.command[2].lower() not in ("admin","member"):
            return await m.reply_text("Format: <code>.allow ai admin</code>")
        await app.db.set_permission(m.chat.id,m.command[1],m.command[2].lower(),m.command[0].lower()=="allow")
        await m.reply_text("✅ Permission diperbarui.")

    @app.on_message(filters.command("autoreply", prefixes="."))
    async def autoreply(_,m):
        if not await command_allowed(app,m,"autoreply"): return
        a=m.text.split(maxsplit=2)
        if len(a)<3: return await m.reply_text("Format: <code>.autoreply keyword balasan</code>")
        await app.db.add_autoreply(m.chat.id,a[1],a[2]); await m.reply_text("✅ Auto-reply disimpan.")

    @app.on_message(filters.command(["delreply","listreply"], prefixes="."))
    async def replies(_,m):
        if not await command_allowed(app,m,"autoreply"): return
        if m.command[0].lower()=="delreply":
            if len(m.command)<2: return
            await app.db.del_autoreply(m.chat.id,m.command[1]); return await m.reply_text("✅ Dihapus.")
        rows=await app.db.list_autoreplies(m.chat.id)
        if not rows: return await m.reply_text("📋 Belum ada auto-reply.")
        await m.reply_text("📋 <b>Auto Reply</b>\n\n"+"\n".join(f"• <code>{r['keyword']}</code> → {r['response'][:100]}" for r in rows))

    @app.on_message(filters.command("random", prefixes="."))
    async def random_cmd(_,m):
        if not await command_allowed(app,m,"random"): return
        a=m.text.split(maxsplit=1)
        if len(a)<2: return await m.reply_text("Contoh: <code>.random merah|biru|hijau</code>")
        c=[x.strip() for x in a[1].split("|") if x.strip()]
        if c: await m.reply_text("🎲 "+random.choice(c))

    @app.on_message(filters.command("texttools", prefixes="."))
    async def texttools(_,m):
        if not await command_allowed(app,m,"texttools"): return
        a=m.text.split(maxsplit=1)
        if len(a)<2: return await m.reply_text("Contoh: <code>.texttools halo dunia</code>")
        t=a[1]; await m.reply_text(f"🔤 <b>Text Tools</b>\nKarakter: {len(t)}\nKata: {len(t.split())}\nUPPER: {t.upper()}\nLOWER: {t.lower()}")

    @app.on_message(filters.command("qr", prefixes="."))
    async def qr(_,m):
        if not await command_allowed(app,m,"qr"): return
        a=m.text.split(maxsplit=1)
        if len(a)<2: return await m.reply_text("Contoh: <code>.qr https://example.com</code>")
        try:
            import qrcode
            bio=io.BytesIO(); bio.name="qr.png"; qrcode.make(a[1]).save(bio,"PNG"); bio.seek(0); await m.reply_photo(bio)
        except Exception as e: await m.reply_text(f"❌ QR gagal: <code>{type(e).__name__}</code>")

    @app.on_message(filters.command("song", prefixes="."))
    async def song(_,m):
        if not await command_allowed(app,m,"song"): return
        a=m.text.split(maxsplit=1)
        if len(a)<2: return await m.reply_text("Contoh: <code>.song Numb Linkin Park</code>")
        q=urllib.parse.quote_plus(a[1])
        await m.reply_text(f"🎵 <b>{a[1]}</b>\n\n🔎 YouTube:\nhttps://www.youtube.com/results?search_query={q}")

    @app.on_message(filters.command("movie", prefixes="."))
    async def movie(_,m):
        if not await command_allowed(app,m,"movie"): return
        a=m.text.split(maxsplit=1)
        if len(a)<2: return await m.reply_text("Contoh: <code>.movie Avengers</code>")
        if not app.cfg.tmdb_api_key: return await m.reply_text("❌ Isi <code>TMDB_API_KEY</code> di Railway Variables.")
        try:
            import aiohttp
            async with aiohttp.ClientSession() as s:
                async with s.get("https://api.themoviedb.org/3/search/multi",params={"api_key":app.cfg.tmdb_api_key,"query":a[1],"language":"id-ID"},timeout=15) as r: data=await r.json()
            x=(data.get("results") or [None])[0]
            if not x: return await m.reply_text("❌ Film tidak ditemukan.")
            await m.reply_text(f"🎬 <b>{x.get('title') or x.get('name') or a[1]}</b>\n\n{x.get('overview') or '-'}")
        except Exception as e: await m.reply_text(f"❌ Movie error: <code>{type(e).__name__}</code>")

    @app.on_message(filters.command("game", prefixes="."))
    async def game(_,m):
        if not await command_allowed(app,m,"game"): return
        n=random.randint(1,6); await app.db.score_add(m.chat.id,m.from_user.id,m.from_user.first_name or "User",points=n,xp=n*10)
        await m.reply_text(f"🎮 Kamu mendapat <b>{n}</b> poin.\nGunakan <code>.score</code> untuk leaderboard.")

    @app.on_message(filters.command("score", prefixes="."))
    async def score(_,m):
        if not await command_allowed(app,m,"game"): return
        rows=await app.db.leaderboard(m.chat.id)
        if not rows: return await m.reply_text("🏆 Belum ada skor.")
        await m.reply_text("🏆 <b>Leaderboard</b>\n\n"+"\n".join(f"{i+1}. {r['name']} — {r['points']} poin (XP {r['xp']})" for i,r in enumerate(rows)))

    @app.on_message(filters.command("quiz", prefixes="."))
    async def quiz(_,m):
        if not await command_allowed(app,m,"quiz"): return
        questions=[("Ibukota Indonesia?","jakarta"),("2 + 2 = ?","4"),("Planet merah?","mars"),("5 x 3 = ?","15"),("Bahasa resmi Indonesia?","bahasa indonesia")]
        q,a=random.choice(questions)
        await app.db.set_setting if False else None
        await m.reply_text(f"🧩 <b>Quiz</b>\n{q}\n\nBalas jawabanmu. (Jawaban benar: disimpan hanya di handler sederhana.)")
        app.quiz_answers=getattr(app,"quiz_answers",{}); app.quiz_answers[m.chat.id]=(a,m.from_user.id)

    @app.on_message(filters.command("translate", prefixes="."))
    async def translate(_,m):
        if not await command_allowed(app,m,"translate"): return
        a=m.text.split(maxsplit=2)
        if len(a)<3: return await m.reply_text("Format: <code>.translate en halo dunia</code>")
        target,text=a[1],a[2]
        if not app.cfg.gemini_api_key: return await m.reply_text("❌ GEMINI_API_KEY belum diisi.")
        from handlers.ai import gemini_generate
        try: out=await gemini_generate(app,f"Terjemahkan ke bahasa {target}. Hanya berikan hasil terjemahan:\n{text}")
        except Exception as e: return await m.reply_text(f"❌ Translate gagal: <code>{type(e).__name__}</code>")
        await m.reply_text(out[:4000])

    @app.on_message(filters.command("ai", prefixes="."))
    async def ai(_,m):
        if not await command_allowed(app,m,"ai"): return
        a=m.text.split(maxsplit=1)
        if len(a)<2: return await m.reply_text("Contoh: <code>.ai jelaskan fotosintesis</code>")
        from handlers.ai import gemini_generate
        try: out=await gemini_generate(app,a[1])
        except Exception as e: return await m.reply_text(f"❌ AI gagal: <code>{type(e).__name__}</code>")
        await m.reply_text(out[:4000])

    @app.on_message(filters.command("textgen", prefixes="."))
    async def textgen(_,m):
        if not await command_allowed(app,m,"textgen"): return
        a=m.text.split(maxsplit=1)
        if len(a)<2: return await m.reply_text("Contoh: <code>.textgen buat caption jualan</code>")
        from handlers.ai import gemini_generate
        try: out=await gemini_generate(app,a[1],system="Buat teks yang rapi dan langsung bisa dipakai.")
        except Exception as e: return await m.reply_text(f"❌ Textgen gagal: <code>{type(e).__name__}</code>")
        await m.reply_text(out[:4000])

    @app.on_message(filters.command("ocr", prefixes="."))
    async def ocr(_,m):
        if not await command_allowed(app,m,"ocr"): return
        if not app.cfg.ocr_api_key: return await m.reply_text("❌ Isi OCR_API_KEY di Railway Variables.")
        source=m.reply_to_message if m.reply_to_message and (m.reply_to_message.photo or m.reply_to_message.document) else None
        if not source: return await m.reply_text("Reply foto/gambar dengan <code>.ocr</code>.")
        try:
            path=await app.download_media(source,in_memory=True)
            import aiohttp
            form=aiohttp.FormData(); form.add_field("apikey",app.cfg.ocr_api_key); form.add_field("language","eng"); form.add_field("file",path.getvalue(),filename="image.jpg",content_type="application/octet-stream")
            async with aiohttp.ClientSession() as s:
                async with s.post("https://api.ocr.space/parse/image",data=form,timeout=45) as r: data=await r.json()
            text="\n".join(x.get("ParsedText","") for x in data.get("ParsedResults",[])).strip()
            await m.reply_text("👁️ <b>OCR</b>\n\n"+(text or "Tidak ada teks terdeteksi.")[:4000])
        except Exception as e: await m.reply_text(f"❌ OCR gagal: <code>{type(e).__name__}</code>")

    @app.on_message(filters.command(["addtarget","deltarget","targets","jashare"], prefixes="."))
    async def jashare(_,m):
        if not await _owner(app,m): return
        cmd=m.command[0].lower()
        if cmd=="addtarget":
            if len(m.command)<2 or not m.command[1].lstrip("-").isdigit(): return await m.reply_text("Format: <code>.addtarget CHAT_ID label</code>")
            label=" ".join(m.command[2:]) if len(m.command)>2 else ""
            await app.db.add_target(app.cfg.owner_id,int(m.command[1]),label); return await m.reply_text("✅ Target tersimpan.")
        if cmd=="deltarget":
            if len(m.command)<2: return
            await app.db.del_target(app.cfg.owner_id,int(m.command[1])); return await m.reply_text("✅ Target dihapus.")
        if cmd=="targets":
            rows=await app.db.targets(app.cfg.owner_id)
            return await m.reply_text("📢 <b>Targets</b>\n\n"+("\n".join(f"• <code>{r['chat_id']}</code> {r['label'] or ''}" for r in rows) if rows else "Belum ada target."))
        if len(m.command)<2: return await m.reply_text("Format: <code>.jashare pesan yang dikirim</code>")
        rows=await app.db.targets(app.cfg.owner_id)
        sent=0
        for r in rows:
            try: await app.send_message(r["chat_id"],"📢 "+m.text.split(maxsplit=1)[1]); sent+=1
            except Exception: pass
        await m.reply_text(f"✅ Terkirim ke {sent}/{len(rows)} target.")

    @app.on_message(filters.command("antispam", prefixes="."))
    async def antispam(_,m):
        if not await _owner(app,m): return
        if len(m.command)>=2 and m.command[1].lower() in ("on","off"):
            await app.settings.set(m.chat.id,"antispam","enabled",m.command[1].lower()=="on")
            return await m.reply_text("✅ Anti Spam diperbarui.")
        await m.reply_text("Format: <code>.antispam on</code> / <code>.antispam off</code>")
