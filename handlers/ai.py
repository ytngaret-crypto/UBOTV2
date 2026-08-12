import aiohttp

async def gemini_generate(app, prompt, system=None):
    key=app.cfg.gemini_api_key
    if not key:
        raise RuntimeError("GEMINI_API_KEY belum diisi")
    model=app.cfg.gemini_model
    url=f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body={"contents":[{"role":"user","parts":[{"text":((system+"\n\n") if system else "")+prompt}]}]}
    async with aiohttp.ClientSession() as s:
        async with s.post(url, params={"key":key}, json=body, timeout=60) as r:
            data=await r.json()
            if r.status >= 400:
                raise RuntimeError(data.get("error",{}).get("message",f"HTTP {r.status}"))
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError,IndexError,TypeError):
        raise RuntimeError("Respons Gemini tidak berisi teks")
