from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from features import FEATURES, CATEGORIES

def btn(text, data):
    return InlineKeyboardButton(text=text, callback_data=data)

def main_menu(is_owner=True):
    rows = []
    for index, title in enumerate(CATEGORIES):
        rows.append([btn(title, f"cat:{index}")])
    rows.append([
        btn("📊 Status", "status"),
        btn("➕ Tambahkan ke Grup", "addgroup"),
    ])
    rows.append([
        btn("💎 Beli Premium", "premium"),
    ])
    if is_owner:
        rows.append([
            btn("⚙️ Settings", "settings"),
            btn("🔐 Permissions", "perm:menu"),
        ])
    return InlineKeyboardMarkup(rows)

def category_menu(title, visible_features=None):
    features = list(CATEGORIES.get(title, []))
    if visible_features is not None:
        allowed = set(visible_features)
        features = [f for f in features if f in allowed]
    rows = []
    for i in range(0, len(features), 2):
        row = []
        for feature in features[i:i+2]:
            row.append(btn(FEATURES[feature][0], f"feat:{feature}"))
        rows.append(row)
    if not features:
        rows.append([btn("ℹ️ Tidak ada fitur aktif", "noop")])
    rows.append([btn("⬅️ Menu Utama", "home")])
    return InlineKeyboardMarkup(rows)

def permission_menu():
    features = [f for f in FEATURES if f != "dashboard"]
    rows = []
    for i in range(0, len(features), 2):
        rows.append([btn(f"⚙️ {FEATURES[f][0]}", f"pfeat:{f}") for f in features[i:i+2]])
    rows.append([btn("⬅️ Menu Utama", "home")])
    return InlineKeyboardMarkup(rows)

def feature_permission_menu(feature, admin_allowed, member_allowed):
    return InlineKeyboardMarkup([
        [
            btn(f"Admin {'✅' if admin_allowed else '❌'}", f"toggle:{feature}:admin"),
            btn(f"Member {'✅' if member_allowed else '❌'}", f"toggle:{feature}:member"),
        ],
        [btn("⬅️ Permissions", "perm:menu"), btn("🏠 Menu", "home")]
    ])

def feature_detail_menu(feature):
    return InlineKeyboardMarkup([
        [btn("⬅️ Kategori", f"backfeature:{feature}")],
        [btn("🏠 Menu Utama", "home")]
    ])
