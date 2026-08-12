from pyrogram import enums
from pyrogram.types import CallbackQuery
from features import FEATURES, CATEGORIES
from ui import main_menu, category_menu, permission_menu, feature_permission_menu, feature_detail_menu

def register_callback_handlers(app):
    @app.on_callback_query()
    async def callbacks(_,q:CallbackQuery):
        try:
            data=q.data or ""
            msg=q.message
            uid=q.from_user.id if q.from_user else 0
            role=await app.db.get_role(uid)
            chat_id=msg.chat.id if msg and msg.chat else uid

            if data=="noop":
                return await q.answer("Tidak ada fitur aktif.",show_alert=True)
            if data=="home":
                await q.answer()
                if msg: await msg.edit_text(f"🤖 <b>{app.cfg.bot_name}</b>\n\n📋 <b>Semua Fitur</b>\nPilih kategori:",reply_markup=main_menu(role=="owner"))
                return
            if data=="status":
                await q.answer()
                if msg:
                    me=await app.get_me()
                    text=f"📊 <b>Status UBot</b>\n\n🤖 {app.cfg.bot_name}\n👤 {me.first_name}\n🆔 <code>{me.id}</code>\n🔐 Role kamu: <b>{role}</b>"
                    await msg.edit_text(text,reply_markup=main_menu(role=="owner"))
                return
            if data=="addgroup":
                await q.answer("Buka link Add to Group dari profil Telegram UBot.",show_alert=True); return
            if data=="premium":
                await q.answer()
                if msg: await msg.edit_text("💎 <b>Premium</b>\n\nPaket premium dapat kamu atur melalui payment Owner.\nGunakan /hubungi Owner untuk pembelian.",reply_markup=main_menu(role=="owner"))
                return
            if data=="settings":
                if role!="owner": return await q.answer("Khusus Owner.",show_alert=True)
                await q.answer()
                if msg: await msg.edit_text("⚙️ <b>Settings</b>\n\nGunakan <code>.settings</code>, <code>.set fitur setting nilai</code>, <code>.on fitur</code>, atau <code>.off fitur</code>.",reply_markup=main_menu(True))
                return
            if data=="perm:menu":
                if role!="owner": return await q.answer("Khusus Owner.",show_alert=True)
                await q.answer()
                if msg: await msg.edit_text("🔐 <b>Permissions</b>\nPilih fitur:",reply_markup=permission_menu())
                return
            if data.startswith("cat:"):
                try: title=list(CATEGORIES)[int(data.split(":")[1])]
                except Exception: return await q.answer("Kategori tidak ditemukan.",show_alert=True)
                visible=[]
                for f in CATEGORIES[title]:
                    if role=="owner" or await app.db.permission(chat_id,f,role): visible.append(f)
                await q.answer()
                if msg: await msg.edit_text(f"📂 <b>{title}</b>\n\nPilih fitur:",reply_markup=category_menu(title,visible))
                return
            if data.startswith("feat:"):
                f=data.split(":",1)[1]
                if f not in FEATURES or f=="dashboard": return await q.answer("Fitur tidak ditemukan.",show_alert=True)
                if role!="owner" and not await app.db.permission(chat_id,f,role): return await q.answer("Fitur belum diizinkan.",show_alert=True)
                label,desc=FEATURES[f]
                commands={"ban":".ban (reply)","unban":".unban (reply)","mute":".mute (reply)","unmute":".unmute (reply)","autoreply":".autoreply keyword balasan","antispam":".antispam on","translate":".translate en teks","ai":".ai pertanyaan","ocr":".ocr (reply foto)","music":".song judul lagu","movie":".movie judul","game":".game","quiz":".quiz","random":".random a|b|c","textgen":".textgen prompt","texttools":".texttools teks","jashare":".jashare pesan","payment":".pay","qr":".qr link"}
                await q.answer()
                if msg: await msg.edit_text(f"{label}\n\n{desc}\n\n💻 <b>Command:</b> <code>{commands.get(f,'-')}</code>",reply_markup=feature_detail_menu(f))
                return
            if data.startswith("pfeat:"):
                if role!="owner": return await q.answer("Khusus Owner.",show_alert=True)
                f=data.split(":",1)[1]
                if f not in FEATURES or f=="dashboard": return await q.answer("Fitur tidak ditemukan.",show_alert=True)
                a=await app.db.permission(chat_id,f,"admin"); m=await app.db.permission(chat_id,f,"member")
                await q.answer()
                if msg: await msg.edit_text(f"⚙️ <b>{FEATURES[f][0]}</b>\n\nAtur akses:",reply_markup=feature_permission_menu(f,a,m))
                return
            if data.startswith("toggle:"):
                if role!="owner": return await q.answer("Khusus Owner.",show_alert=True)
                _,f,r=data.split(":")
                cur=await app.db.permission(chat_id,f,r)
                await app.db.set_permission(chat_id,f,r,not cur)
                await q.answer("Permission diperbarui.")
                if msg: await msg.edit_reply_markup(feature_permission_menu(f,await app.db.permission(chat_id,f,"admin"),await app.db.permission(chat_id,f,"member")))
                return
            if data.startswith("backfeature:"):
                f=data.split(":",1)[1]
                title=next((t for t,fs in CATEGORIES.items() if f in fs),None)
                if not title: return await q.answer()
                visible=[x for x in CATEGORIES[title] if role=="owner" or await app.db.permission(chat_id,x,role)]
                await q.answer()
                if msg: await msg.edit_text(f"📂 <b>{title}</b>",reply_markup=category_menu(title,visible))
                return
            await q.answer("Tombol tidak dikenal.",show_alert=True)
        except Exception:
            try: await q.answer("Menu error. Coba .menu lagi.",show_alert=True)
            except Exception: pass
