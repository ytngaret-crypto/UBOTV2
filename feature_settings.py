FEATURE_SETTINGS = {}
def parse_value(raw):
    v=raw.strip(); low=v.lower()
    if low in ("on","true","yes","aktif"): return True
    if low in ("off","false","no","nonaktif"): return False
    try: return int(v)
    except ValueError: return v
